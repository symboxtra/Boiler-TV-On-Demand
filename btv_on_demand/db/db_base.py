from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable

class BtvDatabaseError(Exception):
    pass

class BtvDatabase(ABC):
    '''
    Abstract class for database-specific implementations.

    Any queries that do not require obvious database-specific
    extensions are implemented in the base class. Queries that require
    database-specific implementation are marked as abstract and must be
    implemented by the child class.
    '''

    @staticmethod
    def factory(db_type):
        if (db_type == 'sqlite'):
            from .db_sqlite import BtvSqliteDatabase
            return BtvSqliteDatabase()
        else:
            raise BtvDatabaseError(f"Unknown database backend '{db_type}'")

    def __init__(self):

        self.db = None
        self.db_config = {}

    @abstractmethod
    def _begin(self):
        '''
        Start a transaction.
        '''
        pass

    @abstractmethod
    def _execute(self, qstring, parameters=[]):
        '''
        Execute the query string with the given parameters.

        return: List of dictionary-like objects that can be indexed via column name.
        '''
        pass

    @abstractmethod
    def _commit(self):
        '''
        Finalize transaction.
        '''
        pass

    @abstractmethod
    def result_to_simple_type(self, result) -> Dict[str, Any]:
        '''
        Convert the list of dictionary-like objects returned by `_execute`
        into simple Python types (i.e. dict and list).
        '''
        pass

    @abstractmethod
    def insert_category(self, name, ext_category_id=None) -> int:
        pass

    @abstractmethod
    def insert_person(self, name) -> int:
        pass

    @abstractmethod
    def insert_content(self, api_fields) -> int:
        pass

    @abstractmethod
    def associate_category(self, content_id, category_id):
        pass

    @abstractmethod
    def associate_star(self, content_id, person_id):
        pass

    @abstractmethod
    def associate_director(self, content_id, person_id):
        pass

    def _first_result(self, results):
        if (len(results) == 0):
            return None

        return results[0]

    def get_category_by_id(self, id) -> Dict[str, Any]:
        qstring = f'''SELECT * FROM category WHERE id = ?'''
        results = self._execute(qstring, [id])

        return self._first_result(results)

    def get_category_by_ext_id(self, ext_id) -> Dict[str, Any]:
        qstring = f'''SELECT * FROM category WHERE ext_category_id = ? ORDER BY first_seen DESC'''
        results = self._execute(qstring, [ext_id])

        return self._first_result(results)

    def get_category_by_name(self, name) -> Dict[str, Any]:
        qstring = '''SELECT * FROM category WHERE name = ?'''
        results = self._execute(qstring, [name])

        return self._first_result(results)

    def get_person_by_id(self, id) -> Dict[str, Any]:
        qstring = f'''SELECT * FROM person WHERE id = ?'''
        results = self._execute(qstring, [id])

        return self._first_result(results)

    def get_person_by_name(self, name) -> Dict[str, Any]:
        qstring = '''SELECT * FROM person WHERE name = ?'''
        results = self._execute(qstring, [name])

        return self._first_result(results)

    def get_content_by_id(self, id) -> Dict[str, Any]:
        qstring = f'''SELECT * FROM content WHERE id = ?'''
        results = self._execute(qstring, [id])

        return self._first_result(results)

    def get_content_by_ext_content_id(self, ext_id) -> Dict[str, Any]:
        qstring = f'''SELECT * FROM content WHERE ext_content_id = ?'''
        results = self._execute(qstring, [ext_id])

        return self._first_result(results)

    def get_content_by_title(self, title) -> Iterable[Dict[str, Any]]:
        qstring = '''SELECT * FROM content WHERE title = ?'''
        return self._execute(qstring, [title])

    def get_content_by_category(self, category_id) -> Iterable[Dict[str, Any]]:

        qstring = '''
            SELECT *
            FROM category_content AS cc
                LEFT JOIN content AS c ON c.id = cc.content_id
            WHERE
                cc.category_id <> ?
        '''
        return self._execute(qstring, [category_id])

    def get_content_by_star(self, person_id) -> Iterable[Dict[str, Any]]:

        qstring = '''
            SELECT *
            FROM starring AS s
                LEFT JOIN content AS c ON c.id = s.content_id
            WHERE
                s.person_id = ?
        '''
        return self._execute(qstring, [person_id])

    def get_content_by_director(self, person_id) -> Iterable[Dict[str, Any]]:

        qstring = '''
            SELECT *
            FROM directed_by AS d
                LEFT JOIN content AS c ON c.id = d.content_id
            WHERE
                d.person_id = ?
        '''
        return self._execute(qstring, [person_id])

    def get_license_period(self, content_id, start, end) -> Dict[str, Any]:

        qstring = '''
            SELECT *
            FROM license
            WHERE
                content_id = ?
                AND license_start = ?
                AND license_end = ?
        '''
        results = self._execute(qstring, [content_id, start, end])

        return self._first_result(results)

    def get_license_periods_by_content(self, content_id) -> Iterable[Dict[str, Any]]:

        qstring = '''SELECT * FROM license WHERE content_id = ?'''
        return self._execute(qstring, [content_id])
