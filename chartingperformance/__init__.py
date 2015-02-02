from flask import Flask
from chartingperformance.database import db_session
from flask.ext.cors import CORS

app = Flask(__name__)
app.config.from_object('chartingperformance.default_settings')
app.config.from_envvar('HOMEPERFORMANCE_SETTINGS')

CORS(app, resources=r'/api/*', allow_headers='Content-Type')

import chartingperformance.routing

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
