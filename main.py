import os
import base64
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)

def access_idealista_api():
    API_TOKEN = os.getenv('IDEALISTA_TOKEN')
    API_SECRET = os.getenv('IDEALISTA_SECRET')
    API_ACCESS = f"{API_TOKEN}:{API_SECRET}"
    print(API_ACCESS)

    encoded_access = base64.b64encode(API_ACCESS.encode("ascii")).decode("ascii")

    headers = {
        "Authorization": f"Basic {encoded_access}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }

    params = {
        "grant_type": "client_credentials",
        "scope": "read"
    }

    response = requests.post("https://api.idealista.com/oauth/token",
                             headers = headers,
                             params = params
                             )

    return json.loads(response.text)['access_token']

def retrieve_rent_url(pagination):
    base_url = "https://api.idealista.com/3.5/"
    locale = "es"
    operation = "sale"
    property_type = "homes"
    center = '41.645826,2.739923'
    distance = '80000'
    sort = 'asc'
    maxPrice = 350000
    bedrooms = "4"
    bathrooms = "2"

    url = (f"{base_url}{locale}/search?"
           f"operation={operation}&"
           f"propertyType={property_type}&"
           f"center={center}&"
           f"distance={distance}&"
           f"sort={sort}&"
           f"maxItems=50&"
           f"numPage={pagination}&"
           f"maxPrice={maxPrice}&"
           f"bedrooms={bedrooms}&"
           f"bathrooms={bathrooms}")

    return url
     
def retrieve_data(url, token):
    headers = {
        'Content-Type': 'Content-Type: multipart/form-data;',
        'Authorization': f'Bearer {token}'
    }

    result = requests.post(url, headers = headers)

    if result.status_code != 429:
        return json.loads(result.text)
    
    return None

def access_notion_api():
    API_TOKEN = os.getenv('NOTION_TOKEN')

    headers = {
        "Authorization": "Bearer " + API_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    return headers

def update_data_notion(headers, data):
    url = f"https://api.notion.com/v1/pages"

    formatted_data = {
        "Adreça": {
            "title": [
                {
                    "text": {
                        "content": data[2]
                    }
                }
            ]
        },
        "Preu": {
            "number": int(data[1])
        },
        "URL": {
            "url": data[0]
        },
        "Lavabos": {
            "select": {
                "name": str(data[3])
            }
        },
        "Habitacions": {
            "select": {
                "name": str(data[4])
            }
        },
    }

    payload = {"parent": { "database_id": os.getenv('DATABASE_ID') }, "properties": formatted_data}
    response = requests.post(url, json=payload, headers=headers)

    if response:
        print("Added successfully!")

if __name__ == "__main__":
    results = None
    access_token_idealista = access_idealista_api()
    headers = access_notion_api()

    url = retrieve_rent_url(1)

    first_results = retrieve_data(url, access_token_idealista)

    if not first_results:
        print("Couldn't obtain results")
    else:
        data = first_results['elementList']

        for i in range(2, first_results['totalPages']+1):
            results = retrieve_data(url, access_token_idealista)

        if not results:
            print("Couldn't obtain results")
        else:
            for property in results['elementList']:
                update_data_notion(headers, data=[property['url'], property['price'], property['address'], property['bathrooms'], property['rooms']])
