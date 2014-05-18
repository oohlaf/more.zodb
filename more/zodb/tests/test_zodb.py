import pytest

from more.zodb.main import zodb_tween_factory, db_from_uri, get_zodb_root


def test_get_zodb_root():
    request = DummyRequest()
    databases = {}
    primary_db = DummyDB(database_name='primary', databases=databases)
    secondary_db = DummyDB(database_name='secondary', databases=databases)
    request.primary_zodb_conn = primary_db.open()

    primary_root = get_zodb_root(request)
    assert primary_root is request.primary_zodb_conn.root()

    secondary_root = get_zodb_root(request, 'secondary')
    assert secondary_root is secondary_db.open().root()


def test_db_from_uri():
    from ZODB.MappingStorage import MappingStorage
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


def test_zodb_handler_exception():
    def handler(request):
        raise NotImplementedError

    publish = zodb_tween_factory(DummyApp(), handler)
    with pytest.raises(NotImplementedError):
        publish(DummyRequest())


def test_zodb_handler():
    request = DummyRequest()
    response = DummyResponse()

    def db_from_uri(uri, dbname, dbmap):
        return DummyDB(database_name=dbname, databases=dbmap)

    def handler_test_get_zodb_root(request):
        req_conn = request.primary_zodb_conn
        assert req_conn.closed is False
        assert req_conn.transaction_manager.aborted is False

        primary_root = get_zodb_root(request)
        assert primary_root is req_conn.root()
        secondary_root = get_zodb_root(request, 'secondary')
        assert secondary_root is req_conn.get_connection('secondary').root()

        return response

    app = DummyApp()
    publish = zodb_tween_factory(app, handler_test_get_zodb_root,
                                 db_from_uri=db_from_uri)
    result = publish(request)
    assert result is response
    assert request.primary_zodb_conn.transaction_manager.aborted is True
    assert request.primary_zodb_conn.closed is True


class DummySettingsSectionContainer(object):
    def __init__(self):
        self.zodb = DummyZODBSettingSection()


class DummyZODBSettingSection(object):
    def __init__(self):
        self.primary = 'memory://one'
        self.secondary = 'memory://two'


class DummyApp(object):
    def __init__(self):
        self.settings = DummySettingsSectionContainer()


class DummyRequest(object):
    path = '/'

    def __init__(self):
        self.environ = {}


class DummyResponse(object):
    def __init__(self, status='200 OK', headers=None):
        self.status = status
        if headers is None:
            headers = {}
        self.headers = headers


class DummyDB(object):
    def __init__(self, database_name='unnamed', databases={}):
        databases[database_name] = self
        self.database_name = database_name
        self.databases = databases
        self.connection = DummyConnection(db=self)

    def open(self):
        return self.connection

    def setActivityMonitor(self, am):
        self.am = am


class DummyConnection(object):
    closed = False

    def __init__(self, db):
        self.transaction_manager = DummyTransactionManager()
        self.db = db
        self.connections = self.db.databases
        self.db_root = {}

    def close(self):
        self.closed = True

    def get_connection(self, name):
        return self.connections[name].open()

    def root(self):
        return self.db_root


class DummyTransactionManager(object):
    aborted = False

    def abort(self):
        self.aborted = True
