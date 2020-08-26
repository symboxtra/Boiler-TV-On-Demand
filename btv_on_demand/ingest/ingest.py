from urllib.parse import urljoin

import requests

from ..db import BtvDatabase

BASE_URL = 'https://boilertvondemand-housing-purdue-edu.swankmp.net/jsonapi/'

class BtvError(Exception):
    pass

def get_categories():

    url = urljoin(BASE_URL, 'GetCategories')

    try:
        resp = requests.get(url)
        resp_json = resp.json()
    except Exception as e:
        raise BtvError('Could not process request. Are you connected to the VPN?', e)

    return resp_json

def get_content():

    url = urljoin(BASE_URL, 'GetAllContent')
    try:
        resp = requests.get(url)
        resp_json = resp.json()
    except Exception as e:
        raise BtvError('Could not process request. Are you connected to the VPN?', e)

    return resp_json

def ingest_categories(db: BtvDatabase, categories):

    for category in categories:

        category_id = category['CategoryId']
        category_name = category['Name']

        db.insert_category(category_name, id=category_id)

def ingest_contents(db: BtvDatabase, contents):

    for content in contents:

        content_id = db.insert_content(content)

        for category_id in content['CategoryIds']:
            db.associate_category(content_id, category_id)

        for actor in content['Actors']:
            person_id = db.insert_person(actor)
            db.associate_star(content_id, person_id)

        for director in content['Directors']:
            person_id = db.insert_person(director)
            db.associate_director(content_id, person_id)
