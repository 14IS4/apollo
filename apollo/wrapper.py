from subprocess import call
from os import chdir, getenv
from os.path import join

from apollo import utils, log, directory, slack
from apollo.secrets import GIT, DBT, PG
from apollo.config import VARS
from apollo.connections import postgres
from apollo.utils import Timer, Increment

pg = postgres()
run_time = Timer()
run_time.start()
step = Increment()
dbt_count = Increment()

branch = VARS['branch']
override = VARS['override']
client = VARS['client']
run_result = VARS['run_result']
failed_at_command = VARS['failed_at_command']
failed_at_step = VARS['failed_at_step']
skip = VARS['skip']
step_attachments = VARS['step_attachments']
failed_tables = VARS['failed_tables']
environment = VARS['environment']
bucket_name = VARS['bucket_name']
schema = PG['SCH']

job_id = VARS['job_id']
run_type_id = VARS['run_type_id']
ran_by = VARS['ran_by']

def new_run(run_type: int, job: int, ran: str) -> int:
    qry = f"""
    INSERT INTO runs (run_type_id, job_id, ran_by) 
    VALUES ({run_type}, {job}, '{ran}') RETURNING id;
    """
    run_id = int(pg.return_one(qry))
    return run_id

def get_dbt_commands(job_id: int) -> str:
    qry = f"SELECT commands FROM jobs WHERE id = {job_id};"
    commands = pg.return_one(qry)
    return commands

def get_job_name(job_id: int) -> str:
    qry = f"SELECT job_name FROM jobs WHERE id = {job_id};"
    job_name = pg.return_one(qry)
    return job_name

def update_run(run_id: int, run_result: str, completed_at: str, total_run_time: float) -> None:
    sql = f"""
        UPDATE runs
        SET run_result = '{run_result}',
            completed_at = '{completed_at}',
            total_run_time_sec = {total_run_time}
        WHERE id = {run_id};
    """
    try:
        pg.query(sql)
    except Exception as e:
        print(e)

job_name = get_job_name(job_id)
run_id = new_run(run_type_id, job_id, ran_by)
git_clone = f"git clone --progress {GIT['CLONE_URL']} {VARS['dbt_root']}"
dbt_cmd = getenv("DBT_CMD") if job_id == 1 else get_dbt_commands(job_id)

directory.override_files('profiles.yml', 
                    {"DBT_USER": DBT['USER'], "DBT_PASSWORD": DBT['PASS'], "SCHEMA": schema, "RUN_ID": run_id}, 
                    join(VARS['user_root'], '.dbt', 'profiles.yml'))
if override:
    directory.override_files(f'{override}.yml', {"DB_NAME": client}, join(VARS['dbt_root'], 'models', 'sources.yml'))

def merge_commands() -> str:
    git_cmd = f"git checkout {branch},"
    git_cmd += dbt_cmd
    return git_cmd

def run_step(run_cmd: str) -> None:
    global failed_at_command
    global failed_at_step
    global run_result
    global failed_tables
    global skip
    t = Timer()
    for cmd in run_cmd.split(','):
        step.add()
        t.start()
        command_type, step_type = utils.command_types(cmd)
        if command_type == 'dbt':
            dbt_count.add()
        if command_type == 'unk':
            skip = True
        elif command_type == 'dbt' and dbt_count == 1:
            unused_models_list = directory.unused_models(dbt_cmd)
            if unused_models_list:
                utils.threaded(directory.remove_unused_models, unused_models_list)
        if not skip:
            filename = f"{run_id}_{step.value}.log"
            filepath = f"{join(VARS['apollo_root'], filename)}"
            s3_path = f"s3://{bucket_name}/{run_id}/console/{filename}"
            started = utils.get_timestamp()
            with open(filepath, 'w') as f:
                call(cmd.split(), stdout=f, stderr=f)
            completed = utils.get_timestamp()
            if command_type == 'dbt' and directory.is_error(filepath):
                skip = True
                failed_at_step = step.value
                failed_at_command = cmd
                result = 'error'
                run_result = 'error'
            else:
                result = 'success'
            if step_type == 'source':
                failed_tables = log.freshness_details(run_id, step.value)
            directory.upload_to_s3('console', filepath, filename, run_id)
            if command_type == 'dbt':
                directory.upload_to_s3('logs', join(VARS['dbt_root'], 'logs', 'dbt.log'), filename, run_id)
                directory.upload_to_s3('artifacts', join(VARS['dbt_root'], 'target', 'run_results.json'), f"{run_id}_{step.value}_run_results.json", run_id)
        else:
            result = 'skipped'
        model_path = cmd.split()[-1].split('.')[0]
        model = model_path if step_type == 'run' else ''
        db = directory.get_db_from_model(model_path) if step_type == 'run' and cmd.split()[-1].split('.')[-1] == '*' else ''
        # Override to remove username and password from Git Clone statement
        cmd = f"git clone {GIT['URL']}" if step_type == 'clone' else cmd
        step_time = t.stop()
        if command_type == 'git':
            message = f"{step_type.capitalize()} {command_type.capitalize()} {f'Branch {branch}' if step_type == 'checkout' else 'Repository'} ({result.capitalize()} in {utils.seconds_formatter(step_time)})"
        else:
            message = f"Invoke dbt with `{cmd.lower()}` ({result.capitalize()} in {utils.seconds_formatter(step_time)})"
        step_attachments.append(slack.add_attachment(result, message))
        # Load Console table
        console = utils.var_to_dict(run_id=run_id, step=step.value, 
                                    job_id=job_id, file_path=s3_path)
        pg.dict_to_table(console, 'console')
        # Load Logs Detailed table
        logs_detailed = utils.var_to_dict(run_id=run_id, step=step.value,
                                        step_result=result, command_type=command_type,
                                        step_type=step_type, step_command=cmd, db=db, 
                                        sch=schema, model=model, execution_time=step_time, 
                                        started_at=started, completed_at=completed)
        pg.dict_to_table(logs_detailed, 'logs_detailed')

def main() -> None:
    started_at = utils.get_timestamp()
    run_step(git_clone)
    chdir(VARS['dbt_root'])
    run_cmd = merge_commands() if not branch == 'master' else dbt_cmd
    run_step(run_cmd)
    completed_at = utils.get_timestamp()
    total_run_time = run_time.stop()
    directory.upload_artifacts(run_id)
    # Load Logs table
    logs = utils.var_to_dict(run_id=run_id, total_steps=step.value,
                            run_commands=dbt_cmd, failed_at_step=failed_at_step,
                            failed_at_command=failed_at_command,
                            started_at=started_at, completed_at=completed_at)
    pg.dict_to_table(logs, 'logs')
    # Update Runs table
    update_run(run_id, run_result, completed_at, total_run_time)
    if run_result == 'success':
        trigger = f'Kicked off from UI by {ran_by}' if run_type_id == 1 else 'Scheduled'
        slack_message = slack.add_header(run_result, run_id, job_name, environment, trigger, utils.seconds_formatter(total_run_time))
        slack_message['attachments'].extend(step_attachments)
        slack.post_message(slack_message)
    pg.close()