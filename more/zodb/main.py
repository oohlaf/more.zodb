import morepath

from more.transaction.main import transaction_tween_factory
from zodburi import resolve_uri
from ZODB import DB
from ZODB.ActivityMonitor import ActivityMonitor


app = morepath.App()


def get_zodb_root(request, dbname='primary'):
    primary_conn = request.primary_zodb_conn
    if dbname is 'primary':
        return primary_conn.root()

    conn = primary_conn.get_connection(dbname)
    return conn.root()


@app.setting(section='zodb', name='primary')
def get_primary_uri():
    return 'file://Data.fs?connection_cache_size=20000'


def db_from_uri(uri, dbname, dbmap, resolve_uri=resolve_uri):
    storage_factory, dbkw = resolve_uri(uri)
    dbkw['database_name'] = dbname
    storage = storage_factory()
    return DB(storage, databases=dbmap, **dbkw)


@app.tween_factory(over=transaction_tween_factory)
def zodb_tween_factory(app, handler):
    databases = {}
    for name, uri in vars(app.settings.zodb).items():
        db = db_from_uri(uri, name, databases)
        db.setActivityMonitor(ActivityMonitor())
    primary_db = databases['primary']

    def zodb_tween(request):
        primary_conn = primary_db.open()
        request.primary_zodb_conn = primary_conn
        response = handler(request)
        # The transaction tween should have committed or aborted the
        # transaction. Changes after that are aborted.
        primary_conn.transaction_manager.abort()
        # Closing the primary connection also closes any secondaries opened.
        primary_conn.close()
        return response

    return zodb_tween
