# home-performance-flask

This repo houses a complete rewrite of the [home-performance-ang](https://github.com/netplusdesign/home-performance-ang) backend from PHP to Python and Flask.

The new version of the Angular frontend is at [home-performance-ang-flask](https://github.com/netplusdesign/home-performance-ang-flask).

MySQL is still maintained as the database, but I'm using SQLAlchemy in hopes that this will make it easier to try out new DBs in the future.

Database setup scripts at [home-performance-ops](https://github.com/netplusdesign/home-performance-ops).

A running version of the API is available at: [lburks.pythonanywhere.com/api/houses](http://lburks.pythonanywhere.com/api/houses)

## Installation -- Dev

Make sure database is already setup and populated with test data.

Create a virtual environment

`virtualenv env`

Activate the environment

`. env/bin/activate`

Install flask, flask-sqlalchemy and your database driver. I'm using mySQL.

If you have a similar setup then you can run,

`pip install -r requirements.txt`

Otherwise, you can selectively install the following.

`pip install Flask`

`pip install flask-sqlalchemy`

`pip install mysql-python`

`pip install simplejson`

`pip install -U flask-cors`

`pip install moment`

Start the Flask HTTP server.

`python run.py`

You should see:  * Running on http://127.0.0.1:5000/

Point browser at, http://127.0.0.1:5000/api/houses

And, if you've setup test data, you should see a json list of at least one house.

## Installation -- PythonAnywhere

Create a new database on the database tab.

Upload a backup of your local database.

From the MySQL console:

`source filename.sql`

Update default_settings.py with username, password, database and host info.

Add a new web app under the Web tab.

In the path, enter...

/home/name/chartingperformance

Check the WSGI configuration and make sure the app is imported correctly. It should look like this:

```python
from chartingperformance import app as application
```

Upload files to the chartingperformance folder.

Install 2 packages that are not standard on PythonAnywhere. Use the --user flag.

`pip install --user momment`

`pip install -U --user flask-cors`

Edit __init__.py and comment or remove the last 2 lines:

```python
#if __name__ == '__main__':
#    app.run(debug=True)
```

I also had to comment out this line:

```python
#app.config.from_envvar('HOMEPERFORMANCE_SETTINGS')
```

Although in hindsight, could have set the variable in the console. Maybe next time.

Hit refresh on the Web tab, just to make sure everything is ready to go.

Point browser at, http://youraccount.pythonanywhere.com/api/houses


## API reference

### api/houses/

Status: Working

List of houses, only one right now.

### api/houses/:house_id/devices/

Status: Working

List of monitoring devices for selected house

### api/houses/:house_id/circuits/

Status: Working

List of values for all circuits for selected house.

Attibutes - Not implemented

  * start -- date (just date for now, time is not supported)
  * end -- date
  * duation -- i int, combined with hour(s), day(s) or month(s). Examples: 1hour, 24hours, 1month, 2months, 1year 
  * interval -- options are years, months or days

### api/houses/:house_id/circuits/:circuit+circuit+circuit...

Status: Not implemented

List of values for selected circuits for selected house.

Attibutes

  * start -- date (just date for now, time is not supported)
  * duation -- i int, combined with hour(s), day(s) or month(s). Examples: 1month, 2months, 1year 
  * interval -- options are years, months, days or hours

### api/houses/:house_id/temperatures/

Status: Not implemented

List of defaults for Angular app

Should I have an endpoint for circuits and temperatures? Or just serve these from the devices endpoint?

api/houses/:house_id/devices/:device_id/?data=field1+field2+field3

api/houses/0/devices/10/?data=used+solar+net

api/houses/0/devices/5+10/?data=used+solar+net

### api/houses/:house_id/views/defaults/

Status: Working

List of defaults for Angular app

* Attibutes
  * interval -- options are months and days
  
### api/houses/:house_id/views/

Status: Working

The `views` endpoints cater specifically to the needs of the Angular frontend.

List of available views and valid intervals

  * __summary__ -- years, months. Returns date, used, solar, net and hdd.
  * __usage__ -- months, days, hours. Returns date, used and budgeted.
  * __generation__ -- months, days, hours. Returns date, solar and estimated.
  * net -- months, days, hours. Returns ???
  * __basetemp__ -- months, days, hours. Returns date, ashp and hdd.
  * __water__ -- months. Returns date, main, cold, hot, water_heater and water_pump.
  * temperatures -- months, days, hours. Returns date, ???
  * __hdd__ -- months, days, hours. Returns date, hdd and estimated
  * __heatmap__ -- days
  * __chart__ -- hours

### api/houses/:house_id/views/:view/

Status: Working

List of fields for selected view

Attibutes

  * start -- date, range includes start date. (time is ignored). Ex. 2014-12-01
  * end -- date, range does _not_ include end date. (time is ignored). Ex. 2014-12-01
  * duration -- string, time factor added to start, combined with hour(s), day(s) or month(s). Ex. 1month, 2months, 1year (Currently only addative to start date. If supplied, will override end date.)
  * interval -- int, options are years, months or days, hours. Not all intervals work on all views.
  * base -- int, base temperature for 'heat' view only.
  * circuit -- string. See api/houses/:house_id/circuits/

If you do not include start or end, all records will be returned with a limit of 500 records.

Examples

  * [views/summary/?interval=years](http://lburks.pythonanywhere.com/api/houses/0/views/summary/?interval=years)  (yearly/summary view)
  * [views/summary/?start=2014-01-01&duration=1year&interval=months](http://lburks.pythonanywhere.com/api/houses/0/views/summary/?start=2014-01-01&duration=1year&interval=months) (summary for 2014 by month)
  * [views/usage/?start=2014-01-01&duation=1year](http://lburks.pythonanywhere.com/api/houses/0/views/usage/?start=2014-01-01&duation=1year)  (usage summary 2014)
  * [views/usage/?start=2014-01-01&duation=1year&interval=months&circuit=ashp](http://lburks.pythonanywhere.com/api/houses/0/views/usage/?start=2014-01-01&duation=1year&interval=months&circuit=ashp)  (usage for ashp in 2014 by month)
  * views/usage/?start=2014-01-01&duration=1month&interval=days&circuit=ashp  (usage for ashp in Jan 2014 by day) Days not implemented yet.
  
