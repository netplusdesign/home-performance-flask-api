""" Start home performance app with env settings """
from chartingperformance import app

app.config.from_envvar('HOMEPERFORMANCE_SETTINGS')
app.run(host=app.config['HOST'], debug=True)
