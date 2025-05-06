#
#  NEED TO ADD THE FOLLOWING PACKAGES:
#   * snowflake.core
#   * snowflake-ml-python
#
import streamlit as st

import time
from snowflake.snowpark.context import get_active_session
import snowflake.snowpark.functions as F

from snowflake.core import Root
from snowflake.cortex import Complete

session = get_active_session()

st.session_state.active_suggestion = None

slide_window = 7 # how many last conversations to remember. This is the slide window.
DATABASE = "FSI_DEMOS"
SCHEMA = "WEALTH"
SS_NAME = "WEALTH_MEETING_SEARCH"
SS_COLUMNS = ["PAST_MEETING_NOTES"]

MODELS = [
        "llama3.1-405b",
        "llama3.1-70b",
        "mistral-large2",
        "llama3.2-3b", # NEED CROSS REGION CALLS OR TO BE IN AWS US West 2
    ]


st.header("Welcome to the Wealth Insights Hub :house:")

with st.sidebar:
    # Dynamic filters   
    customer = st.selectbox("Customer:", session.table("CUSTOMERS").select("CID").distinct(), placeholder="Please select a Customer ID",
                           format_func=lambda x:session.table("CUSTOMERS").filter(F.col("CID") == x).select_expr("FIRST_NAME || ' ' || LAST_NAME").collect()[0][0])

customer_info = session.table("CUSTOMERS").filter(F.col("CID") == customer).collect()[0]

portfolio_data = session.table("PORTFOLIO_DATA").filter(F.col("CID") == customer)

# relationship_history = session.table("RELATIONSHIP_HISTORY").filter(F.col("CID") == customer)

col1,col2 = st.columns([8, 3])

with col2:
    st.image("https://www.natwest.com/premier-banking/services/_jcr_content/root/responsivegrid/hero/singlearticle_copy_c/article_image.coreimg.82.667.jpeg/1718189924060/nw-prem-photo-woman-using-tablet-in-lounge.jpeg")
with col1:
    st.write("")
    st.write("Helping our customers spend more time focusing on what really matters. Through helping with finances and talking through any concerns, this application helps our colleagues gain faster insights and dive deeper help customers secure the future they want.")

tab1, tab2 = st.tabs(["Wealth 360", "Wealth Advisor Bot :robot_face:"])

## to-add: Target Asset Allocation Mix

with tab1:
    
    with st.expander("Customer Details"):
    
        st.subheader("Customer Details")
        col1,col2 = st.columns(2)
        with col1:  
            st.write("**CID**:", customer_info['CID'])
            st.write("**Date of Birth**:", customer_info['DOB'])
            st.write("**Planned Retirement Age**:", customer_info['PLANNED_RETIREMENT_AGE'])
            st.write("**Domicile**:", customer_info['DOMICILE'])
        with col2:
            st.write("**Customer Name:**", customer_info['FIRST_NAME'], customer_info['LAST_NAME'])
            st.write("**Occupation**:", customer_info['OCCUPATION'])
            st.write("**Account Type**:", customer_info['CUST_TYPE'])
            st.write("**No of Dependents**:", customer_info['DEPENDENTS'])

    with st.expander("Customer Profile"):

        st.subheader("Customer Profile")
        col1,col2 = st.columns(2)
        with col1:
        
            st.write("**Short Term Goals**:")
            st.write(customer_info['SHORT_TERM_GOALS'])
    
            st.write("**Risk Tolerance**:")
            st.write(customer_info['RISK_TOLERANCE'])
        with col2:
            st.write("**Long Term Goals**:")
            st.write(customer_info['LONG_TERM_GOALS'])
            
            st.write("**Investment Interest**:")
            st.write(customer_info['INVESTMENT_INTERESTS'])



    st.subheader('Customer Portfolio Breakdown')

    col1, col2 = st.columns(2)
    with col1:
        st.metric('**Net Asset Value**',portfolio_data.select(F.round(F.sum('AMOUNT'))).collect()[0][0])
    with col2:
        st.metric('**YTD Return (%)**',portfolio_data.select(F.round(F.avg('YTD_RETURN'))).collect()[0][0])
    
    st.bar_chart(portfolio_data,
                x='ASSET_CLASS',
                y='AMOUNT')
    with st.expander("Detailed Portfolio View"):
        st.dataframe(portfolio_data)    

    
with tab2:
    
    def init_messages():
        """
        Initialize the session state for chat messages. If the session state indicates that the
        conversation should be cleared or if the "messages" key is not in the session state,
        initialize it as an empty list.
        """
        if st.session_state.clear_conversation or "messages" not in st.session_state:
            st.session_state.messages = [] # reset_session_state
    
    def init_service_metadata():
        """
        THIS IS NOT USED FOR NOW!
        
        Initialize the session state for cortex search service metadata. Query the available
        cortex search services from the Snowflake session and store their names and search
        columns in the session state.
        """
        if "service_metadata" not in st.session_state:
            services = session.sql("SHOW CORTEX SEARCH SERVICES;").collect()
            service_metadata = []
            if services:
                for s in services:
                    svc_name = s["name"]
                    svc_search_col = session.sql(
                        f"DESC CORTEX SEARCH SERVICE {svc_name};"
                    ).collect()[0]["search_column"]
                    service_metadata.append(
                        {"name": svc_name, "search_column": svc_search_col}
                        # customer
                    )
    
            st.session_state.service_metadata = service_metadata
    
    def init_config_options():
        """
        Initialize the configuration options in the Streamlit sidebar. Allow the user to clear the conversation, toggle debug mode, and toggle the use of
        chat history. Also provide advanced options to select a model
        """
    
        st.sidebar.button("Clear conversation", key="clear_conversation")
        st.sidebar.toggle("Debug", key="debug", value=False)
        st.sidebar.toggle("Use chat history", key="use_chat_history", value=True)
    
        with st.sidebar.expander("Advanced options"):
            st.selectbox("Select model:", MODELS, key="model_name")

        st.sidebar.expander("Session State").write(st.session_state)

    #########
    # Cortex search
    #########
    def query_cortex_search_service(query: str,
                                    limit: int = 10,
                                    # experimental={"dropIrrelevantResults": True},
                                 ):

        search_service = root.databases[DATABASE].schemas[SCHEMA].cortex_search_services[SS_NAME]

        resp = search_service.search(query=query, columns=SS_COLUMNS, filter={"@eq": {"CID": f"{customer}" } }, limit=limit)
        
        return resp.json() 
    
    def get_chat_history():
    #Get the history from the st.session_state.messages according to the slide window parameter
        
        chat_history = []
        
        start_index = max(0, len(st.session_state.messages) - slide_window)
        for i in range (start_index , len(st.session_state.messages) -1):
             chat_history.append(st.session_state.messages[i])
    
        return chat_history
    
    def summarize_question_with_history(chat_history, question):
    # To get the right context, use the LLM to first summarize the previous conversation
    # This will be used to get embeddings and find similar chunks in the docs for context
    
        prompt = f"""
            Based on the chat history below and the question, generate a query that extend the question
            with the chat history provided. The query should be in natual language. 
            Answer with only the query. Do not add any explanation.
            
            <chat_history>
            {chat_history}
            </chat_history>
            <question>
            {question}
            </question>
            """
        
        sumary = Complete(st.session_state.model_name, prompt)   
    
        if st.session_state.debug:
            st.sidebar.text("Summary to be used to find similar chunks in the docs:")
            st.sidebar.caption(sumary)
    
        sumary = sumary.replace("'", "")
    
        return sumary


    def create_prompt (myquestion):

        if st.session_state.use_chat_history:
            chat_history = get_chat_history()
    
            if chat_history != []: #There is chat_history, so not first question
                search_question = summarize_question_with_history(chat_history, myquestion)
            else:
                search_question = myquestion
        else:
            chat_history = ""
            search_question = myquestion
        
        prompt_context = query_cortex_search_service(search_question)
        
        prompt = f"""
               You are an expert chat assistance that extracs information from the CONTEXT provided
               between <context> and </context> tags.
               You offer a chat experience considering the information included in the CHAT HISTORY
               provided between <chat_history> and </chat_history> tags..
               When ansering the question contained between <question> and </question> tags
               be concise and do not hallucinate. 
               If you don´t have the information just say so.
               
               Do not mention the CONTEXT used in your answer.
               Do not mention the CHAT HISTORY used in your asnwer.
    
               Only anwer the question if you can extract it from the CONTEXT provideed.
               
               <chat_history>
               {chat_history}
               </chat_history>
               <context>          
               {prompt_context}
               </context>
               <question>  
               {myquestion}
               </question>
               Answer: 
               """
        
        return prompt
    
    def call_complete(myquestion):

        prompt = create_prompt(myquestion)
        response = Complete(st.session_state.model_name, prompt)
        
        return response
        
    def main():

        st.title(f":speech_balloon: Chat with your meetings Notes")
        
        init_service_metadata()
        init_config_options()
        init_messages()
        
        icons = {"assistant": "❄️", "user": "👤", "analyst": "❄️",}
        
        disable_chat = (
            "service_metadata" not in st.session_state
            or len(st.session_state.service_metadata) == 0
        )
        
        # Display messages in chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar=icons[message["role"]]):
                st.markdown(message["content"], unsafe_allow_html=True)
        
        chat_placeholder = st.empty()
        
        if question := st.chat_input("Ask a question..."):
            with chat_placeholder.container(height=400, border=False):
            
                # Display user message in chat message container
                with st.chat_message("user", avatar=icons["user"]):
                    st.markdown(question)
                
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": question, "type": "text"})
    
                # Display assistant response in chat message container
                with st.chat_message("assistant", avatar=icons["assistant"]):
                    with st.spinner("Thinking..."):
                        time.sleep(1)  # Spinner needs extra time to render properly
                        response = call_complete(question)
                        formatted_response = response.replace("'", "")

                        st.markdown(formatted_response, unsafe_allow_html=True)
        
                        # Once the stream is over, update chat history
                        st.session_state.messages.append({"role": "assistant",
                                                      "content": formatted_response, 
                                                        "type": "text"})
    
    if __name__ == "__main__":
        root = Root(session)
        main()
