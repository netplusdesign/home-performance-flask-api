config = {
    'user' : 'web',
    'password' : 'test',
    'host' : '127.0.0.1',
    'database' : 'home_performance_dev'
}

DEBUG = True
SECRET_KEY = 'secretsecretsecret'
DATABASE_URI = 'mysql://%s:%s@%s/%s' % (config['user'],\
    config['password'], config['host'], config['database'])
HOST = '0.0.0.0'
