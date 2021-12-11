config = {
    'user' : 'root',
    'password' : 'secret',
    'host' : 'mariadb',
    'database' : 'home_performance_dev'
}
# database host: mariadb or mysql56

DEBUG = True
HOST = '0.0.0.0'
PORT = 5000
SECRET_KEY = 'secretsecretsecret'
DATABASE_URI = 'mariadb+mariadbconnector://%s:%s@%s/%s' % (config['user'],\
    config['password'], config['host'], config['database'])
