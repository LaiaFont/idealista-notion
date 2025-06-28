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
    operation = "rent"
    property_type = "homes"
    center = '41.38879,2.15899'
    distance = '4000'
    sort = 'asc'
    maxPrice = 1600
    bedrooms = "2,3,4"
    bathrooms = "1,2"

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

    return json.loads(result.text)

def access_notion_api():
    API_TOKEN = os.getenv('NOTION_TOKEN')

    headers = {
        "Authorization": "Bearer " + API_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    return headers

def update_data_notion(headers, data, num_pages=None):
    url = f"https://api.notion.com/v1/databases/{os.getenv('DATABASE_ID')}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    formatted_data = {
        "url": [],
        "preu": {
            "number": data[1]
        },
        "adreça": {
            "text": {
                "content": data[2]
            }
        } ,
        "lavabos": {
            "select": {
                'name': data[3]
            }
        },
        "habitacions": {
            "select": {
                'name': data[4]
            }
        },
    }

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    print(data)

if __name__ == "__main__":
    # access_token_idealista = access_idealista_api()

    # url = retrieve_rent_url(1)

    # first_results = retrieve_data(url, access_token_idealista)
    # data = first_results['elementList']

    # for i in range(2, first_results['totalPages']+1):
    #     # results = retrieve_data(url, access_token_idealista)
    
    headers = access_notion_api()

    update_data_notion(headers, data=['https://www.idealista.com/inmueble/100482025/', '1250', 'El Poble Sec - Parc de Montjuïc, Barcelona', 2, 2])

