import os
import requests
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)

def access_api(name):
    API_TOKEN = os.getenv(f'{name.upper()}_TOKEN')
    print(API_TOKEN)

if __name__ == "__main__":
    access_api("notion")