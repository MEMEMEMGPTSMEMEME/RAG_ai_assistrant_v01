# gpts_config/utils.py

import os
from dotenv import load_dotenv

load_dotenv()

def get_env_path(var_name, default):
    return os.getenv(var_name, default)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
