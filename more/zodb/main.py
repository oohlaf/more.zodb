import morepath


app = morepath.App()


@app.setting(section='zodb', name='zodbconn_uri')
def get_zodbconn_uri():
    return 'file://%(here)s/Data.fs?connection_cache_size=20000'


@app.tween_factory()
def zodb_tween_factory(app, handler):
    uri = app.settings.zodb.zodbconn_uri

    def zodb_tween(request):
        response = handler(request)
        return response

    return zodb_tween
