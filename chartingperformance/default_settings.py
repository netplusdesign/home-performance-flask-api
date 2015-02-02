config = {
    'user' : 'web', 
    'password' : 'test',
    'host' : '127.0.0.1',
    'database' : 'home_performance_dev'
}

db_connect = 'mysql://%s:%s@%s/%s' % (config['user'], config['password'], config['host'], config['database'])

DEBUG = True
SECRET_KEY = 'sectretsecretsecret'
