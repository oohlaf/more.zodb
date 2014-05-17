import pytest

from more.zodb.main import zodb_tween_factory, db_from_uri
from ZODB.MappingStorage import MappingStorage


def test_zodb_handler_exception():
    def handler(request):
        raise NotImplementedError

    publish = zodb_tween_factory(DummyApp(), handler)
    with pytest.raises(NotImplementedError):
        publish(DummyRequest())


def test_zodb_handler():
    response = DummyResponse()

    def handler(request):
        return response

    app = DummyApp()
    publish = zodb_tween_factory(app, handler)
    result = publish(DummyRequest())
    assert result is response


def test_db_from_uri():
    storage = MappingStorage()

    def resolve_uri(uri):
        def storagefactory():
            return storage
        return storagefactory, {}

    databases = {}
    db = db_from_uri('uri', 'name', databases, resolve_uri=resolve_uri)
    assert db._storage is storage
    assert db.database_name is 'name'
    assert db.databases is databases


class DummySettingsSectionContainer(object):
    def __init__(self):
        self.zodb = DummyZODBSettingSection()


class DummyZODBSettingSection(object):
    def __init__(self):
        self.primary = 'memory://'


class DummyApp(object):
    def __init__(self):
        self.settings = DummySettingsSectionContainer()


class DummyRequest(object):
    path = '/'

    def __init__(self):
        self.environ = {}
        self.made_seekable = 0

    def make_body_seekable(self):
        self.made_seekable += 1


class DummyResponse(object):
    def __init__(self, status='200 OK', headers=None):
        self.status = status
        if headers is None:
            headers = {}
        self.headers = headers
