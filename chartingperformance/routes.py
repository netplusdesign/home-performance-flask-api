""" Flask routing """
# pylint: disable=no-member
from chartingperformance import app
from chartingperformance import db_session

from chartingperformance.models import Houses
from chartingperformance.models import MonitorDevices
from chartingperformance.models import EnergyMonthly
from chartingperformance.models import EnergyHourly
from chartingperformance.models import LimitsHourly

from chartingperformance.views.circuit import CircuitDict
from chartingperformance.views.summary import Summary
from chartingperformance.views.generation import Generation
from chartingperformance.views.usage import Usage
from chartingperformance.views.hdd import Hdd
from chartingperformance.views.temperature import Temperature
from chartingperformance.views.water import Water
from chartingperformance.views.basetemp import Basetemp
from chartingperformance.views.heatmap import Heatmap
from chartingperformance.views.chart import Chart

from flask import request, jsonify, url_for, make_response

from sqlalchemy import func

@app.errorhandler(404)
def not_found(error):
    """ Return page not found error in json. """
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/api/houses/', methods=['GET'])
def get_houses():
    """ Return list of houses. """

    return jsonify(houses=get_houses_all())

@app.route('/api/houses/<house_id>/', methods=['GET'])
def get_house(house_id):
    """ Return details for house X. """

    return jsonify(house=get_house_details(house_id))

@app.route('/api/houses/<house_id>/devices/', methods=['GET'])
def get_devices(house_id):
    """ Return list of devices for house X. """

    return jsonify(devices=get_devices_all(house_id))

@app.route('/api/houses/<house_id>/circuits/', methods=['GET'])
def get_circuits(house_id):
    """ Return list of circuits for house X. """

    circuits = CircuitDict(house_id)

    return circuits.get_response()

@app.route('/api/houses/<house_id>/views/', methods=['GET'])
def views(house_id):
    """ Return list of available views for house X. """

    return jsonify(views=get_views(house_id))

@app.route('/api/houses/<house_id>/views/default/', methods=['GET'])
def setup(house_id):
    """ Return default values for houses X views. """

    interval = request.args.get('interval', 'months')

    if 'month' in interval:
        return jsonify(years=get_years(house_id),
                       asof=get_asof_date(house_id),
                       house=get_house_details(house_id))
    elif 'day' in interval:
        return jsonify(limits=get_limits(house_id))
    else:
        return jsonify(error='Interval \'%s\' does not exist' % interval)

@app.route('/api/houses/<house_id>/views/summary/', methods=['GET'])
def view_summary(house_id):
    """ Return summary view for house X. """

    view = Summary(request.args, house_id)

    return view.get_response()

@app.route('/api/houses/<house_id>/views/generation/', methods=['GET'])
def view_generation(house_id):
    """ Return generation view for house X. """

    view = Generation(request.args, house_id)

    return view.get_response()

@app.route('/api/houses/<house_id>/views/usage/', methods=['GET'])
def view_usage(house_id):
    """ Return usage view for house X. """

    view = Usage(request.args, house_id)

    return view.get_response()

@app.route('/api/houses/<house_id>/views/hdd/', methods=['GET'])
def view_hdd(house_id):
    """ Return hdd view for house X. """

    view = Hdd(request.args, house_id)

    return view.get_response()

@app.route('/api/houses/<house_id>/views/temperature/', methods=['GET'])
def view_temperature(house_id):
    """ Return temperature view for house X. """

    view = Temperature(request.args, house_id)

    return view.get_response()

@app.route('/api/houses/<house_id>/views/water/', methods=['GET'])
def view_water(house_id):
    """ Return water view for house X. """

    view = Water(request.args, house_id)

    return view.get_response()

@app.route('/api/houses/<house_id>/views/basetemp/', methods=['GET'])
def view_heat(house_id):
    """ Return basetemp view for house X. """

    view = Basetemp(request.args, house_id)

    return view.get_response()

@app.route('/api/houses/<house_id>/views/heatmap/', methods=['GET'])
def view_heatmap(house_id):
    """ Return heatmap daily view for house X. """

    view = Heatmap(request.args, house_id)

    return view.get_response()

@app.route('/api/houses/<house_id>/views/chart/', methods=['GET'])
def view_chart(house_id):
    """ Return chart hourly view for house X. """

    view = Chart(request.args, house_id)

    return view.get_response()


def get_houses_all():
    """ Return array of houses. """

    houses = db_session.query(Houses).all()

    json_items = []
    for house in houses:
        data = {'name': house.name,
                'sname': house.sname,
                'house_id': house.house_id,
                'url': url_for('get_house', house_id=house.house_id, _external=True)}
        json_items.append(data)

    return json_items

def get_house_details(house_id):
    """ Return details for house X in json. """

    house = db_session.query(Houses). \
        filter(Houses.house_id == house_id).one()

    return {'name': house.name,
            'sname': house.sname,
            'id': house.house_id,
            'devices': url_for('get_devices', house_id=house.house_id, _external=True),
            'circuits': url_for('get_circuits', house_id=house.house_id, _external=True),
            'views': url_for('views', house_id=house.house_id, _external=True)}

def get_devices_all(house_id):
    """ Return array of devices for house X. """

    devices = db_session.query(MonitorDevices). \
        filter(Houses.house_id == house_id).all()

    json_items = []
    for device in devices:
        data = {'name': device.name,
                'id': device.device_id}
        json_items.append(data)

    return json_items

def get_years(house_id):
    """ Return array of valid years of energy data for house X. """

    years = db_session.query(EnergyMonthly.date). \
        filter(EnergyMonthly.house_id == house_id). \
        group_by(func.year(EnergyMonthly.date)). \
        order_by(EnergyMonthly.date)

    json_items = []
    for year in years:
        json_items.append(str(year[0].year))

    return json_items

def get_asof_date(house_id):
    """ Return latest date of data as string for house X. """

    asof = db_session.query(LimitsHourly.end_date). \
        filter(LimitsHourly.house_id == house_id).one()

    return str(asof.end_date.strftime("%Y-%m-%d"))

def get_limits(house_id):
    """ Return deails of data limits for house X. Used mainlt in chart view. """

    limits = db_session.query(LimitsHourly). \
        filter(EnergyHourly.house_id == house_id).one()

    return {'used_max': limits.used_max,
            'solar_min': limits.solar_min,
            'outdoor_deg_min': limits.outdoor_deg_min,
            'outdoor_deg_max': limits.outdoor_deg_max,
            'hdd_max': limits.hdd_max,
            'start_date': str(limits.start_date),
            'end_date': str(limits.end_date)}

def get_views(house_id):
    """  Return list of endpoints """

    return [
        url_for('setup', house_id=house_id, _external=True),
        url_for('view_summary', house_id=house_id, _external=True),
        url_for('view_generation', house_id=house_id, _external=True),
        url_for('view_usage', house_id=house_id, _external=True),
        url_for('view_hdd', house_id=house_id, _external=True),
        url_for('view_water', house_id=house_id, _external=True),
        url_for('view_heatmap', house_id=house_id, _external=True),
        url_for('view_chart', house_id=house_id, _external=True)
    ]
