from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

API_KEY = os.environ.get('API_KEY')
