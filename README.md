# Apollo

#### Description

The current intent of apollo is being ran from inside a docker container and to provide a wrapper around the [dbt cli](https://docs.getdbt.com/dbt-cli/cli-overview/). This tool will aid us in moving away from [dbt Cloud](https://cloud.getdbt.com), all of the functionality has been recreated to have feature parity and not degrade the experience when moving towards our own tool. 

#### dbt Cloud Limitations

- Was not meant for running ad-hoc jobs very easily, had to setup an ad-hoc scheduled job and run manually.
- Limited environment for easily working in different branches.
- No ability to parameterize a run for a standard datasource i.e. Pulse-Netsuite would always point to a given database and we need the ability to plug whatever customer we want in order to keep one model.

---

#### Intent

Apollo was built to complete the ongoing SaaS efforts in order to get us to a completely automated state. In order to acheive that, a few things needed to be addressed to allow for more automation and better integration. There are also few things that dbt does that makes it a little harder for a multi-tenant approach. One of the biggest things needing to be addressed were the static yaml files that are required to run dbt ex. profiles.yml or sources.yml. These changes were addressed with apollo and are generated at run time with a use of template files. 

We also needed a way to deeply integrate dbt in the current flow, this means being able to run dbt from Rapid after the job completes. With dbt Cloud we could have triggered an API call but the information we are able to get out of the API is very limited with what we need. The state we are able to acheive now is calling dbt after the extract and load command completes successfully, with the ability to catch failures from the jobs we can pass those back to Rapid in order to re-run automatically.

---

#### Run Environment

Currently an AWS Lambda function with an API Gateway route sits in front of Fargate, when the API is triggered and passed variables the Lambda function will create Fargate task. This decouples the evironment from any UI so it can be integrated wherever needed. 

Scheduled Jobs can be created from the UI and those are deployed as scheduled tasks on our Data Engineering Fargate ECS Cluster through cron.

Ad-hoc jobs are just sent directly to a new container through the API call and ran through Fargate.

---

#### Features over dbt Cloud

- Adds dynamic buildouts of static yaml files i.e. can run multiple customers with the same model
- Removes any models that aren't being used in the current run
- Additional logging specifically targeted towards freshness tests, if a test fails tables will be sent in Slack notification
- Major cost savings over dbt Cloud, we don't have to pay per developer anymore for access
- More to come...

---

#### Installation

There are two easy methods of installation via [pip](https://pip.pypa.io/en/stable/)

```
pip3 install git+https://${URL}/apollo.git
```

or

```
git clone git@${URL}/apollo.git
cd apollo/
pip3 install -e .
```

#### Required Environment Variables

```
$ACCOUNT // Snowflake Account
$ACCESS_KEY // AWS Access Key normally provided by PG DB
$SECRET_KEY // AWS Secret Key normally provided by PG DB
$GIT_USER // Normally passed from UI
$GIT_PASS // Normally passed from UI
$GIT_URL // Normally passed from UI
$DBT_USER // dbt service account user for Snowflake normally provided by PG DB
$DBT_PASSWORD // dbt service account password for Snowflake normally provided by PG DB
$WEBHOOK_URL // URL for Slack channel to notify
$PG_HOST // Following PG variables are for the logging DB
$PG_USER
$PG_PASS
$PG_DB
$PG_PORT
$PG_SCH

```

#### Optional Environment Variables

```
$JOB_ID // Defaults to 1 "Ad-Hoc" if not provided
$OVERRIDE // If an override is provided client will be used to override sources.yml
$ENVIRONMENT // Used to set overrides in credentials, schema, etc.. 
$BRANCH // Defaults to "master" if not provided
$DBT_CMD // Normally passed by UI for Ad-Hoc job, if a job is pass will retrieve from DB
$RAN_BY // Defaults to Scheduled if not passed will be provided automatically from UI
```

---

#### File Structure

```
apollo
.
├── Dockerfile
├── MANIFEST.in
├── README.md
├── apollo
    ├── __init__.py
    ├── config.py
    ├── connections.py
    ├── directory.py
    ├── log.py
    ├── secrets.py
    ├── slack.py
    ├── templates
        ├── __init__.py
        ├── netsuite.yml
        └── profiles.yml
    ├── utils.py
    └── wrapper.py
├── requirements.txt
├── setup.cfg
├── setup.py
```

---

#### Future State

Apollo will be expanded in the future to include command line functionality that can be installed locally or through docker. The cli integration will be implemented with [Typer](https://github.com/tiangolo/typer) and will give the ability to run and log through a local machine.