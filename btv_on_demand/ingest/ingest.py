from urllib.parse import urljoin

import requests

from ..db import BtvDatabase

BASE_URL = 'https://boilertvondemand-housing-purdue-edu.swankmp.net/jsonapi/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
}

class BtvError(Exception):
    pass

def get_categories():

    url = urljoin(BASE_URL, 'GetCategories')

    try:
        resp = requests.get(url, headers=HEADERS)
        resp_json = resp.json()
    except Exception as e:
        raise BtvError('Could not process request. Are you connected to the VPN?', e)

    return resp_json

def get_content():

    url = urljoin(BASE_URL, 'GetAllContent')
    try:
        resp = requests.get(url, headers=HEADERS)
        resp_json = resp.json()
    except Exception as e:
        raise BtvError('Could not process request. Are you connected to the VPN?', e)

    return resp_json

def ingest_categories(db: BtvDatabase, categories):

    for category in categories:

        ext_category_id = category['CategoryId']
        category_name = category['Name']

        db.insert_category(category_name, ext_category_id=ext_category_id)

def ingest_contents(db: BtvDatabase, contents):

    for content in contents:

        content_id = db.insert_content(content)

        for category_id in content['CategoryIds']:
            db.associate_ext_category(content_id, category_id)

        for actor in content['Actors']:
            person_id = db.insert_person(actor)
            db.associate_star(content_id, person_id)

        for director in content['Directors']:
            person_id = db.insert_person(director)
            db.associate_director(content_id, person_id)

def main_ingest(args):

    import sys
    from datetime import datetime
    from pprint import pprint

    from ..db import BtvDatabase

    print('')
    print(f'Ingest started {datetime.now()}')
    print('---------------------------------------')

    db = BtvDatabase.factory('sqlite')

    categories = get_categories()

    print(f'{len(categories)} categories:')
    pprint(categories)
    print('')
    ingest_categories(db, categories)

    content = get_content()

    print(f'{len(content)} programs:')
    # pprint(content)
    print('Print out omitted')
    print('')
    ingest_contents(db, content)
