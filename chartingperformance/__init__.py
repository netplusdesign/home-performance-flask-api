from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask.ext.cors import CORS

app = Flask(__name__)
app.config.from_object('chartingperformance.default_settings')
app.config.from_envvar('HOMEPERFORMANCE_SETTINGS')

engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

CORS(app, resources=r'/api/*', allow_headers='Content-Type')

import chartingperformance.routes

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
