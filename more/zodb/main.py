import morepath

from zodburi import resolve_uri
from ZODB import DB
from ZODB.ActivityMonitor import ActivityMonitor


app = morepath.App()


@app.setting(section='zodb', name='primary')
def get_primary_uri():
    return 'file://Data.fs?connection_cache_size=20000'


def db_from_uri(uri, dbname, dbmap, resolve_uri=resolve_uri):
    storage_factory, dbkw = resolve_uri(uri)
    dbkw['database_name'] = dbname
    storage = storage_factory()
    return DB(storage, databases=dbmap, **dbkw)


@app.tween_factory()
def zodb_tween_factory(app, handler):
    # TODO Register databases somewhere
    databases = {}
    for name, uri in vars(app.settings.zodb).items():
        db = db_from_uri(uri, name, databases)
        db.setActivityMonitor(ActivityMonitor())

    def zodb_tween(request):
        response = handler(request)
        return response

    return zodb_tween
