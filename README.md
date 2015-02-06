# home-performance-flask

This repo houses a complete rewrite of the [home-performance-ang](https://github.com/netplusdesign/home-performance-ang) backend from PHP to Python and Flask.

The new version of the Angular frontend is at [home-performance-ang-flask](https://github.com/netplusdesign/home-performance-ang-flask).

MySQL is still maintained as the database, but I'm using SQLAlchemy in hopes that this will make it easier to try out new DBs in the future.

Database setup scripts at [home-performance-ops](https://github.com/netplusdesign/home-performance-ops).

A running version of this is setup at: TBD

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

Point browser at, http://127.0.0.1:5000/houses

And, if you've setup test data, you should see a json list of at least one house.

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

Status: Not implemented

The `views` endpoints cater specifically to the needs of the Angular frontend.

List of available views and valid intervals

  * __summary__ -- years, months. Returns date, used, solar, net and hdd.
  * __usage__ -- months, days, hours. Returns date, used and budgeted.
  * __generation__ -- months, days, hours. Returns date, solar and estimated.
  * net -- months, days, hours. Returns ???
  * __heat__ -- months, days, hours. Returns date, ashp and hdd.
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
  * interval -- int, options are years, months or days, hours.
  * base -- int, base temperature for 'heat' view only.
  * circuit -- string. See api/houses/:house_id/circuits/

If you do not include start or end, all records will be returned with a limit of 500 records.

Examples

  * views/summary/?interval=years  (yearly/summary view)
  * views/summary/?start=2014-01-01&duration=1year&interval=months (summary for 2014 by month)
  * views/usage/?start=2014-01-01&duation=1year  (usage summary 2014)
  * views/usage/?start=2014-01-01&duation=1year&interval=months&circuit=ashp  (usage for ashp in 2014 by month)
  * views/usage/?start=2014-01-01&duration=1month&interval=days&circuit=ashp  (usage for ashp in Jan 2014 by day)
  
