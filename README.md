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

```

