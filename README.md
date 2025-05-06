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
