from os import getenv
from os.path import expanduser, join

_DBT_DIR = 'dbt'
_DBT_ROOT = expanduser(f'~/{_DBT_DIR}')
_APOLLO_ROOT = expanduser('~/.apollo')
_JOB_ID = getenv("JOB_ID", 1)

VARS = {
    'apollo_root': _APOLLO_ROOT,
    'template_root': join(_APOLLO_ROOT, 'templates'),
    'user_root': expanduser('~'),
    'dbt_root': _DBT_ROOT,
    'dbt_project': join(_DBT_ROOT, 'dbt_project.yml'),
    'bucket_name': 'company-dbt',
    'branch': getenv("BRANCH", "master"),
    'job_id': _JOB_ID,
    'run_type_id': 1 if _JOB_ID == 1 else 2,
    'override': getenv("OVERRIDE"),
    'client': getenv("CLIENT"),
    'ran_by': getenv("RAN_BY", "Schedule"),
    'environment': getenv("EVIRONMENT", "Production"),
    'webhook_url': getenv("WEBHOOK_URL"),
    'run_result': 'success',
    'failed_at_command': None,
    'failed_at_step': None,
    'skip': False,
    'step_attachments': [],
    'failed_tables': []
}