from os import makedirs
from os.path import exists, join
from importlib.resources import read_binary, is_resource, contents
from apollo.config import VARS

def create_folder(file_path: str) -> None:
    if not exists(file_path):
        makedirs(file_path)

# Create root apollo folder
create_folder(VARS['apollo_root'])

# Create folder to clone dbt project into
create_folder(VARS['dbt_root'])

# Create root template folder
create_folder(VARS['template_root'])

# Move package data to template_root
for content in contents('apollo.templates'):
    if is_resource('apollo.templates', content):
        if content[-4:] == '.yml':
            tmplt = read_binary('apollo.templates', content)
            with open(join(VARS['template_root'], content), 'wb') as f:
                f.write(tmplt)