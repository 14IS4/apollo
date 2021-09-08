from os import makedirs
from os.path import exists, join
from apollo.utils import list_diff
from apollo.config import VARS
from apollo.secrets import AWS

def create_folder(file_path: str) -> None:
    if not exists(file_path):
        makedirs(file_path)

def override_files(template_name: str, template_variables: dict, file_path: str) -> None:
    '''
    Generic override of templated files, takes in a source and destination
    path along with templated variables. Source file must be setup with
    Jinja variables {{ example }} in order to replace values. Template variables
    need to be passed in with a dictionary with Jinja variable in ex: {"jinja_var_name": "example value"}
    '''
    from jinja2 import Environment
    from jinja2 import FileSystemLoader
    templated = Environment(loader=FileSystemLoader(VARS['template_root'])).get_template(template_name).render(template_variables)
    with open(file_path, 'w') as f:
        f.write(templated)

def is_error(filename: str) -> bool:
    '''
    Searches a file (intended to be console output of a dbt command) for an indication
    of an error. Returns true or false depending on what is found. Might have to add
    in more exception handling but this covers the basic use cases.
    '''
    with open(filename, 'r') as f:
        output = f.read()
    if not output.lower().find('error=') == -1:
        return int(output[output.lower().find('error=') + 6:output.lower().find('skip=')].rstrip(' ')) > 0
    elif not output.lower().find('fail') == -1:
        return True
    elif not output.lower().find('error') == -1:
        return True
    else:
        return False

def upload_to_s3(folder: str, filepath: str, filename: str, run_id: int) -> None:
    from boto3 import Session
    session = Session(aws_access_key_id=AWS['ACCESS_KEY'], aws_secret_access_key=AWS['SECRET_KEY'])
    s3 = session.client('s3')
    try:
        s3.upload_file(filepath, VARS['bucket_name'], f"{run_id}/{folder}/{filename}")
    except Exception:
        print("error uploading")

###########################################
##### START OF DBT SPECIFIC FUNCTIONS #####
###########################################

_DBT_ROOT = VARS['dbt_root']
_DBT_PROJ = VARS['dbt_project']

def find_model_path(filename: str) -> str:
    '''
    Finds individual files and returns the models folder that they reside in.
    An example if the following was passed in: dbt run --models test
    This function traverses the dbt project looking for the file test.sql and
    will return the folder name where it exists.
    '''
    from subprocess import Popen
    from subprocess import PIPE
    command = f"find {_DBT_ROOT} -iname {filename}.sql"
    output = Popen(command.split(), stdout=PIPE).communicate()[0].decode()
    return output.split('\n')[0].split('/')[-2]

def remove_unused_models(model: str) -> None:
    from shutil import rmtree
    try:
        rmtree(join(_DBT_ROOT, 'models', model))
    except OSError:
        print(f"Error: folder {join(_DBT_ROOT, 'models', model)} does not exist.")

def unused_models(dbt_cmd: str) -> list:
    from yaml import load
    from yaml import FullLoader
    with open(_DBT_PROJ, 'r') as f:
        yml = load(f, Loader=FullLoader)
    model_base = list(yml['models'])[0]
    all_models = yml['models'][model_base].keys()
    current_models = []
    for cmd in dbt_cmd.split(','):
        model_str = cmd.split()[-1].split('.')
        base_model = model_str[0] if model_str[-1] == '*' else find_model_path(model_str[0])
        for model in all_models:
            if base_model == model:
                current_models.append(model)
    return list_diff(current_models, all_models)

def get_db_from_model(model: str) -> str:
    from yaml import load
    from yaml import FullLoader
    with open(_DBT_PROJ, 'r') as f:
        yml = load(f, Loader=FullLoader)
    model_base = list(yml['models'])[0]
    return yml['models'][model_base][model]['database']

def find_compiled_sql() -> list:
    from subprocess import Popen
    from subprocess import PIPE
    command = f"find {join(_DBT_ROOT, 'target', 'compiled')} -iname *.sql"
    output = Popen(command.split(), stdout=PIPE).communicate()[0].decode()
    return list(filter(None, output.split('\n')))

def upload_artifacts(run_id: int) -> None:
    target = join(VARS['dbt_root'], 'target')
    additional_files = [join(target, 'manifest.json')]
    artifacts = find_compiled_sql()
    artifacts.extend(additional_files)
    for artifact in artifacts:
        upload_to_s3('artifacts', artifact, artifact.replace(target, ''), run_id)
