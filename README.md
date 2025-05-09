# Wealth 360 Demo - The Meeting Notes Version!

This is an automated install version of Mats Stewall [demo](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/mstellwall-demos/-/tree/main/fsi_demos/wealth_360/meeting_notes_version)

## Setup

Open a worksheet, copy/paste this code to have an automatic install:

```SQL
create or replace database FSI_DEMOS;
create or replace schema WEALTH;

CREATE OR REPLACE API INTEGRATION git_api_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/ccarrero-sf/')
  ENABLED = TRUE;

CREATE OR REPLACE GIT REPOSITORY git_repo
    api_integration = git_api_integration
    origin = 'https://github.com/ccarrero-sf/wealth_360';

-- Make sure we get the latest files
ALTER GIT REPOSITORY git_repo FETCH;

EXECUTE IMMEDIATE FROM @FSI_DEMOS.WEALTH.git_repo/branches/main/setup.sql;

```

This script will:
- Use this Git repository to get all data you need
- Will create Snowflake tables
- Will load the tables
- Will copy the semantic file that will be used by Cortex Analyst
- Will install Wealth 360 App

![image](/img/DB.png)

## Questions to ask, in the chat part

Open the Streamlit App (Wealth 360 App) and try these questiosn for Sally Johnson:

- What did we talk about for each of the meetings, give a summarisation for each meeting date
- What was the major concerns Sally had during the 2023-11-13 meeting
- What could be a good followup? (is depended on the question above)

## Instal a Local App to use Cortex Agents API

This section shows how to install a local app that leverages the Cortex Agents API that will be able to interact with both structured (your Snowflake tables) and un-structured data (the content of the meeting notes).

You can create a local conda env. In your terminal run:

```code
conda create -n wealth_360 python=3.11
conda activate wealth_360

pip install streamlit
pip install snowflake-snowpark-python
pip install snowflake.core
pip install snowflake-ml-python
pip install sseclient
```

Copy streamlit_local_app.py to your folder and edit it to add your own parameters:

```python
PRIVATE_KEY_PATH = "/path/to/your/rsa_key.p8"


SNOWFLAKE_ACCOUNT = "YOUR_SNOWFLAKE_ACCOUNT_IDENTIFIER" # e.g., xy12345.us-west-2
SNOWFLAKE_USER = "YOUR_SNOWFLAKE_USER"

# --- Other Snowflake Config (Optional but Recommended) ---
SNOWFLAKE_WAREHOUSE = "YOUR_WAREHOUSE"
SNOWFLAKE_DATABASE = "YOUR_DATABASE"
SNOWFLAKE_SCHEMA = "YOUR_SCHEMA"
SNOWFLAKE_ROLE = "YOUR_ROLE" # Optional: Specify role if needed

# Define Tool Resources, ensure paths/names are valid in your Snowflake account)
# !!! IMPORTANT: Replace placeholder values below !!!
AGENT_TOOL_RESOURCES = {
    "analyst1": { "semantic_model_file": "!! IMPORTANT: Replace placeholder this value !!!" },
    "search1": { "name": "!! IMPORTANT: Replace placeholder this value !!!", "max_results": 10 },
}
```



