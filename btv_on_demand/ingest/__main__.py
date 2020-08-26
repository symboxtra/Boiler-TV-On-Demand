import sys
from pprint import pprint

from ..db import BtvDatabase
from .ingest import (
    get_categories,
    get_content,
    ingest_categories,
    ingest_contents
)

if (__name__ == '__main__'):
    db = BtvDatabase.factory('sqlite')

    try:
        categories = get_categories()
    except Exception as e:
        print('')
        print(e)
        sys.exit(1)

    print(f'{len(categories)} categories:')
    pprint(categories)
    print('')
    print('')
    ingest_categories(db, categories)

    try:
        content = get_content()
    except Exception as e:
        print('')
        print(e)
        sys.exit(1)

    print(f'{len(content)} programs:')
    # pprint(content)
    print('Omitted')
    print('')
    ingest_contents(db, content)
