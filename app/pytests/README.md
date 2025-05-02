# Dependency Map specific tests
The `pytests` folder contains the Dependency Map specific tests.

## Setup
The tests needs to be added to the latest released version of the DCAPT tests:

1. Add the `pytests` folder to the `app` folder
2. Update `jira.yml` (hint: diff vs the "Atlassian version")
   a. Create a 'Personal Access Token' for the 'admin' user
   b. Add the access token as the property: `admin_access_token: <keyvalue>` to `jira.yml`.
   c. Add the entries/modifications marked with `# DM-NOTE`.
3. Three

## On Authorization
Basic authorization does not longer work (from Jira 10.3.0).
Instead, we use "Personal Access Token".
When installing Dependency Map in the target Jira, make sure to create a Personal Access Token for the `admin` user.
This needs to be done for each new target Jira.

## Running pytests manually
To run the Dependency Map specific pytests, configure the virtualenv as for when running `bzt jira.yml`.
Run a single test as follows:
```
cd app
pytest --log-cli-level=INFO pytests/test_flow_create_diagram.py
````
