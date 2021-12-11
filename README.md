# home-performance-flask-api

This is an api to serve home performance history data (electricity and water usage, temperatures) to a frontend like [home-performance-ang-flask](https://github.com/netplusdesign/home-performance-ang-flask).

This project has been upgraded to Python 3.x and MySql 8.

Database setup scripts at [home-performance-ops](https://github.com/netplusdesign/home-performance-ops).

A running version of the API is available at: [netplusdesign.com/homeperformance/api/houses](https://www.netplusdesign.com/homeperformance/api/houses/)

## Installation -- Local Dev

Make sure database is already setup and populated with test data.

Create a virtual environment

`python -m venv env`

Activate the environment

`source env/bin/activate`

Install flask, flask-sqlalchemy and your database driver. I'm using mySQL.

If you have a similar setup then you can run,

`pip install -r requirements.txt`

Start the Flask HTTP server.

`python run.py`

You should see:  * Running on http://127.0.0.1:5000/

Point browser at, http://127.0.0.1:5000/api/houses

And, if you've setup test data, you should see a json list of at least one house.

### Run Tests

`python tests.py`

If you install coverage.py you can see the coverage results, currently at 97%.

`coverage run tests.py`

`coverage html` or whichever method you prefer to view the results.

## Installation -- Docker running on Apple Silicon

You can use an old MySQL database, but can't use the old MySQL driver.

I'm using MariaDB running in its own container. Then I have a base image with the new MariaDB Connector.
This required upgrading to SQLAlchemy 1.4.

Build the base image for the MariaDB Connector. See [home-performance-python-mariadb](https://github.com/netplusdesign/home-performance-python-mariadb). The flask-api project uses this image as a base.

Then build the image for home-performance-flask-api.

```
docker build -t home-performance-flask-api .
```

Then run it.

```
docker run --net dev-network --env-file .env -p 5001:5000  --name flask-api -d home-performance-flask-api
```

## Installation -- FastCGI (Not updated)

You will need flup.

`pip install flup`

Follow your host's instructions for setting up your Python environment. Everyone is different. This may include a `.htaccess` file.

Add a `myapp.fcgi` file to your project directory. See [Flask documentation on FastCGI](https://flask.palletsprojects.com/en/1.1.x/deploying/fastcgi/).

Touch the `myapp.fcgi` file after any updates to code.

## API reference

### api/houses/

Status: Working

List of houses, only one right now.

### api/houses/:house_id/devices/

Status: Working

List of monitoring devices for selected house

### api/houses/:house_id/devices/:device_id

Status: Not implemented

List of values for selected device

Attibutes

  * start -- date, range includes start date. (time is ignored). Ex. 2014-12-01
  * end -- date, range does _not_ include end date. (time is ignored). Ex. 2014-12-01
  * duration -- string, time factor added to start, combined with hour(s), day(s) or month(s). Ex. 1month, 2months, 1year (Currently only addative to start date. If supplied, will override end date.)
  * interval -- int, options are years, months or days, hours. Not all intervals work on all views.
  * fields -- string (CSV) of fields to return. Varies by device.

Fields by device

Devices 0, 1, 2 & 3 - temperature monitors

   * date
   * temperature (degrees Fahrenheit)
   * humidity (%)

Device 4 - TED energy monitor

  * date
  * adjusted_load (wh hourly, kWh daily and monthly)
  * solar
  * used

Device 5 - eMonitor energy monitor

  * all the device 4 circuits, plus...
  * water_heater
  * ashp
  * water_pump
  * dryer
  * washer
  * dishwasher
  * stove

Device 6 & 7 - main & hot water

  * date
  * gallons

Device 8 - Albany HHD

  * date
  * hdd

Device 9 - meter read

  * same as device 4

Device 10 - eGauge energy monitor

  * all the device 5 circuits, plus...
  * refrigerator
  * living_room
  * aux_heat_bedrooms
  * aux_heat_living
  * study
  * barn
  * basement_west
  * basement_east
  * ventilation
  * ventilation_preheat
  * kitchen_recept_rt

Example

  * api/houses/0/devices/10/?fields=used,solar,net

### api/houses/:house_id/circuits/

Status: Working

List all circuits for selected house.

### api/houses/:house_id/circuits/:circuit,circuit,circuit...

Status: Not implemented

List of values for selected circuits for selected house.

Attibutes

  * start -- date, range includes start date. (time is ignored). Ex. 2014-12-01
  * end -- date, range does _not_ include end date. (time is ignored). Ex. 2014-12-01
  * duration -- string, time factor added to start, combined with hour(s), day(s) or month(s). Ex. 1month, 2months, 1year (Currently only addative to start date. If supplied, will override end date.)
  * interval -- int, options are years, months or days, hours. Not all intervals work on all views.

### api/houses/:house_id/temperatures/

Status: Not implemented

List of values for selected

Should I have an endpoint for circuits and temperatures? Or just serve these from the devices endpoint, or both?

api/houses/:house_id/devices/:device_id/?fields=field1,field2,field3

api/houses/0/devices/10/?fields=used,solar,net

api/houses/0/devices/5,10/?fields=used,solar,net

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
  * __usage__ -- years, months, days, hours. Returns date, used and budgeted.
  * __generation__ -- years, months, days, hours. Returns date, solar and estimated.
  * net -- months, days, hours. Returns ???
  * __basetemp__ -- months, days, hours. Returns date, ashp and hdd.
  * __water__ -- years, months. Returns date, main, cold, hot, water_heater and water_pump.
  * temperatures -- years, months, days, hours. Returns date, max, min, average, hdd.
  * __hdd__ -- months, days, hours. Returns date, hdd and estimated
  * __heatmap__ -- days
  * __chart__ -- hours

### api/houses/:house_id/views/:view/

Status: Working

List of fields for selected view

Attributes

  * start -- date, range includes start date. (time is ignored). Ex. 2014-12-01
  * end -- date, range does _not_ include end date. (time is ignored). Ex. 2014-12-01
  * duration -- string, time factor added to start, combined with hour(s), day(s) or month(s). Ex. 1month, 2months, 1year (Currently only additive to start date. If supplied, will override end date.)
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
