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
    def insert_category(self, name, id=None) -> int:
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

    def _get_by_id(self, table, id) -> Dict[str, Any]:
        qstring = f'''SELECT * FROM {table} WHERE id = ?'''
        result = self._execute(qstring, [id])

        if (len(result) == 0):
            return None

        return result[0]

    def get_category_by_id(self, id) -> Dict[str, Any]:
        return self._get_by_id('category', id)

    def get_category_by_name(self, name) -> Dict[str, Any]:
        qstring = '''SELECT * FROM category WHERE name = ?'''
        result = self._execute(qstring, [name])

        if (len(result) == 0):
            return None

        return result[0]

    def get_person_by_id(self, id) -> Dict[str, Any]:
        return self._get_by_id('person', id)

    def get_person_by_name(self, name) -> Dict[str, Any]:
        qstring = '''SELECT * FROM person WHERE name = ?'''
        result = self._execute(qstring, [name])

        if (len(result) == 0):
            return None

        return result[0]

    def get_content_by_id(self, id) -> Dict[str, Any]:
        return self._get_by_id('content', id)

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
        result = self._execute(qstring, [content_id, start, end])

        if (len(result) == 0):
            return None

        return result[0]

    def get_license_periods_by_content(self, content_id) -> Iterable[Dict[str, Any]]:

        qstring = '''SELECT * FROM license WHERE content_id = ?'''
        return self._execute(qstring, [content_id])
