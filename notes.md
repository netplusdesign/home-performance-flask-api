# Notes

## Problems and solutions.

### System could not locate MySQL driver after install

> ImportError: dlopen(/Users/xyz/projects/home-performance-flask/env/lib/python2.7/site-packages/_mysql.so, 2): Library not loaded: libmysqlclient.18.dylib
>   Referenced from: /Users/xyz/projects/home-performance-flask/env/lib/python2.7/site-packages/_mysql.so

This article explained the fix, noted below. http://stackoverflow.com/questions/6383310/python-mysqldb-library-not-loaded-libmysqlclient-18-dylib

`otool -L /Users/xyz/projects/home-performance-flask/env/lib/python2.7/site-packages/_mysql.so`

>/Users/xyz/projects/home-performance-flask/env/lib/python2.7/site-packages/_mysql.so:
>	libmysqlclient.18.dylib (compatibility version 18.0.0, current version 18.0.0)
>	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1197.1.1)
	
`sudo install_name_tool -change libmysqlclient.18.dylib /usr/local/mysql/lib/libmysqlclient.18.dylib /Users/xyz/projects/home-performance-flask/env/lib/python2.7/site-packages/_mysql.so`

Now try it again...

`python run.py`

### But then I was getting serialization to JSON errors.

I found an article that said this would be fixed by installing simplejson. It worked. Does not need to be imported directly.

`pip install simplejson`

### Then I tried to call the API from the Angular app running on another server port. 

> [Error] XMLHttpRequest cannot load http://127.0.0.1:5000/api/houses/0/views/summary/?interval=months&start=2013-01-01&duration=1year. Origin http://127.0.0.1 is not allowed by Access-Control-Allow-Origin. (app, line 0)

So another article suggested installing flask-cors. http://flask-cors.readthedocs.org/en/latest/

`pip install -U flask-cors`

Now it should all work.

`python run.py`

### Dates are more fun with moment!

`pip install moment`

### Trouble with database connections.

I was getting Cross Control Allow Origin error after 5 or 10 minutes of not hitting the server. Error log reported:

`sqlalchemy.exc.OperationalError: (OperationalError) (2013, 'Lost connection to MySQL server during query')`

Conrad Ho at PythonAnywhere suggested this SqlAlchemy solution, [disconnect-handling-pessimistic](http://docs.sqlalchemy.org/en/rel_0_8/core/pooling.html#disconnect-handling-pessimistic).

I added the listens_for recipe and imports to the `__init__.py` file.

Worked like a charm. But it is a bit slow on the first connect.

### Trouble with accessing MySQL from shared host

I wanted a more permanent hosting solution, so I asked a few python friends and one recommended asmallorange.com.

Install went well for everything except MySQL. Support recommended the following which solved the problem.

> You cannot install MySQLdb in virtualenv site-package, because it requires access to GCC to compile native code, which we can't allow on our shared servers. We do have MySQLdb installed globally for you to use, but the default virtualenv was configured to ignore global packages.
  Deleting this file ~/.env/env/lib/python2.7/no-global-site-packages.txt will make that virtualenv environment use the system packages as well as the local packages.

Sort of goes against the whole virtual environment thing, but it works.
