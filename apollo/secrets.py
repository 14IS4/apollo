from os import environ

env = environ.copy()

# Postgres credentials for logs database
PG = {
    "HOST": env["POST_HOST"],
    "USER": env["POST_USER"],
    "PASS": env["POST_PASS"],
    "DB": env["POST_DB"],
    "PORT": env["POST_PORT"],
    "SCH": env["POST_SCHEMA"]
}

# AWS access for S3 to upload artifacts and console output
AWS = {
    "ACCESS_KEY": env["ACCESS_KEY"],
    "SECRET_KEY": env["SECRET_KEY"]
}

# DBT credentials that get passed from the UI
DBT = {
    "USER": env["DBT_USER"],
    "PASS": env["DBT_PASSWORD"]
}

# GIT credentials that get passed from the UI
GIT = {
    "URL": env["GIT_URL"],
    "CLONE_URL": env["GIT_URL"].replace("https://", f'https://{env["GIT_USER"]}:{env["GIT_PASS"]}@')
}