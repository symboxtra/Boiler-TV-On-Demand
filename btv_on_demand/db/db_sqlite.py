import os
import sqlite3

from ..utils import get_resource_path, get_storage_path, parse_time_to_s, safe_walk
from .db_base import BtvDatabase, BtvDatabaseError

class BtvSqliteDatabase(BtvDatabase):

    def __init__(self):

        super().__init__()

        # Decide where to store the database file
        # Priority (high to low): environment, config file, default
        db_path = self.db_config.get('path', get_storage_path('data.db'))

        print(f'Using SQLite database at: {db_path}')

        self.db_path = db_path
        self.is_new_db = not os.path.exists(self.db_path)
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row

        # Database debugging
        # self.db.set_trace_callback(print)

        # if (self.is_new_db):
        self.init_new_database()

    def init_new_database(self):
        '''
        Setup database tables using the schema script.
        '''

        with open(get_resource_path('db/schema-sqlite.sql'), mode='r') as f:
            qstring = f.read()

        self._begin()
        self.db.executescript(qstring)
        self._commit()

        self.is_new_db = False
        print('Initialized SQLite database')

    def _begin(self):
        # Do nothing since transactions are automatic on write with sqlite3
        pass

    def _execute(self, qstring, parameters=[]):
        cursor = self.db.execute(qstring, parameters)
        return cursor.fetchall()

    def _commit(self):
        self.db.commit()

    def result_to_simple_type(self, result):

        # Detect single-row results
        if (len(result) > 0 and type(result[0]) != sqlite3.Row):
            return dict(result)

        # Multi-row results
        else:
            return [dict(row) for row in result]

    def insert_category(self, name, ext_category_id=None):

        self._begin()
        qstring = '''
            INSERT OR IGNORE INTO category (
                ext_category_id,
                name
            ) VALUES (
                ?, ?
            )
        '''
        self._execute(qstring, [ext_category_id, name])
        self._commit()

        category = self.get_category_by_name(name)

        if (category is None):
            print(f'Could not retrieve category after insertion!')
            raise BtvDatabaseError('Category missing after insertion')

        return category['id']

    def insert_person(self, name):

        self._begin()
        qstring = '''
            INSERT OR IGNORE INTO person (
                name
            ) VALUES (
                ?
            )
        '''
        self._execute(qstring, [name])
        self._commit()

        person = self.get_person_by_name(name)

        if (person is None):
            print(f'Could not retrieve person after insertion!')
            raise BtvDatabaseError('Person missing after insertion')

        return person['id']

    def insert_content(self, api_fields):

        self._begin()
        qstring = '''
            INSERT OR REPLACE INTO content (
                id,
                ext_content_id,
                media_item_id,
                film_id,
                permalink_token,
                watchlink_token,
                content_ordinal,
                program_type,
                title,
                description,
                release_year,
                runtime_s,
                runtime_h,
                content_language,
                mpaa_rating,
                ustv_rating,
                encode_type,
                license_start,
                license_end,
                first_seen
            ) VALUES (
                (SELECT id FROM content WHERE ext_content_id = ? AND title = ?),
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                datetime(?),
                datetime(?),
                (SELECT first_seen FROM content WHERE ext_content_id = ? AND title = ?)
            )
        '''

        ext_content_id = api_fields['ContentId']
        runtime_s = parse_time_to_s(api_fields.get('Runtime', None))
        runtime_h = None if runtime_s is None else runtime_s / 60.0 / 60.0
        license_start = api_fields.get('LicenseStartDate', None)
        license_end = api_fields.get('LicenseEndDate', None)

        ratings = api_fields.get('Ratings', [])

        mpaa_filtered = filter(lambda v: v.get('Name', None) == 'MPAA', ratings)
        ustv_filtered = filter(lambda v: v.get('Name', None) == 'US TV', ratings)

        mpaa_rating = next(mpaa_filtered, {}).get('Value')
        ustv_rating = next(ustv_filtered, {}).get('Value')

        self._execute(qstring, [
            ext_content_id,
            api_fields.get('Title', None),
            ext_content_id,
            api_fields['MediaItemID'],
            api_fields['FilmId'],
            api_fields.get('PermalinkToken', None),
            api_fields.get('WatchLinkToken', None),
            api_fields.get('ContentOrdinal', None),
            api_fields.get('ProgramType', None),
            api_fields.get('Title', None),
            api_fields.get('Description', None),
            api_fields.get('ReleaseYear', None),
            runtime_s,
            runtime_h,
            api_fields.get('FilmLanguage', None),
            mpaa_rating,
            ustv_rating,
            api_fields.get('EncodeType', None),
            license_start,
            license_end,
            ext_content_id,
            api_fields.get('Title', None)
        ])

        self._commit()

        content = self.get_content_by_ext_content_id(ext_content_id)

        if (content is None):
            print(f'Could not retrieve content after insertion!')
            raise BtvDatabaseError('Content missing after insertion')

        # Add the license period to keep a history
        content_id = content['id']
        self.insert_license_period(content_id, license_start, license_end)

        return content_id

    def insert_license_period(self, content_id, start, end):
        self._begin()
        qstring = '''
            INSERT OR IGNORE INTO license (
                content_id,
                license_start,
                license_end
            ) VALUES (
                ?,
                datetime(?),
                datetime(?)
            )
        '''
        self._execute(qstring, [
            content_id,
            start,
            end
        ])
        self._commit()

        license = self.get_license_period(content_id, start, end)

        if (license is None):
            print(f'Could not retrieve license after insertion!')
            raise BtvDatabaseError('License period missing after insertion')

        return license['id']

    def associate_category(self, content_id, category_id):
        self._begin()
        qstring = '''
            INSERT OR IGNORE INTO category_content (
                content_id,
                category_id
            ) VALUES (
                ?, ?
            )
        '''
        self._execute(qstring, [
            content_id,
            category_id
        ])
        self._commit()

    def associate_ext_category(self, content_id, ext_category_id):
        category = self.get_category_by_ext_id(ext_category_id)

        if (category is None):
            raise BtvDatabaseError(f'Cannot find category with ID: {ext_category_id}')

        return self.associate_category(content_id, category['id'])

    def associate_star(self, content_id, person_id):
        self._begin()
        qstring = '''
            INSERT OR IGNORE INTO starring (
                content_id,
                person_id
            ) VALUES (
                ?, ?
            )
        '''
        self._execute(qstring, [
            content_id,
            person_id
        ])
        self._commit()

    def associate_director(self, content_id, person_id):
        self._begin()
        qstring = '''
            INSERT OR IGNORE INTO directed_by (
                content_id,
                person_id
            ) VALUES (
                ?, ?
            )
        '''
        self._execute(qstring, [
            content_id,
            person_id
        ])
        self._commit()

    def get_license_period(self, content_id, start, end):
        qstring = '''
            SELECT *
            FROM license
            WHERE
                content_id = ?
                AND (
                    license_start = datetime(?)
                    OR license_start IS NULL
                )
                AND (
                    license_end = datetime(?)
                    OR license_end IS NULL
                )
        '''
        results = self._execute(qstring, [content_id, start, end])

        return self._first_result(results)
