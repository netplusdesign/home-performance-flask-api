""" View classes """
# pylint: disable=no-member
from chartingperformance import db_session

from chartingperformance.models import Houses
from chartingperformance.models import EnergyHourly
from chartingperformance.models import EnergyDaily
from chartingperformance.models import EnergyMonthly
from chartingperformance.models import TemperatureHourly
from chartingperformance.models import HDDHourly
from chartingperformance.models import HDDDaily
from chartingperformance.models import HDDMonthly
from chartingperformance.models import Circuits
from chartingperformance.models import EstimatedMonthly

from flask import jsonify

from sqlalchemy import func
from sqlalchemy.sql import label, and_, or_, text

import re
import moment

class View(object):
    """ Parent View provides common methods. Never used directly. """

    def __init__(self, args):
        self.success = True
        self.regex = re.compile("([0-9]+)([a-zA-Z]+)")
        self.valid_intervals = ['hour', 'day', 'month', 'year'] # also need to validate durations
        if args:
            self.args = self.set_args(args)
        else:
            self.success = False
            self.error = { 'error':'No arguments found.' }
        self.base_query = None

    def filter_query_by_date_range(self, table):
        """ Return original query plus date range filters. """

        if self.args['start'] is not None and self.args['end'] is not None:
            self.base_query = self.base_query.\
                              filter(table.date.between(self.args['start'].date,
                                                        self.args['end'].date))
        elif self.args['start'] is not None:
            self.base_query = self.base_query.\
                              filter(table.date >= self.args['start'].date)
        elif self.args['end'] is not None:
            self.base_query = self.base_query.\
                              filter(table.date < self.args['end'].date)

        return self.base_query

    def filter_query_remove_summer_months(self, table):
        """ Return original query plus filters to remove summer months. """

        self.base_query = self.base_query.\
                          filter(or_(func.month(table.date) < 5,
                                     func.month(table.date) > 9))

        return self.base_query

    def group_query_by_interval(self, table):
        """ Return original query plus grouping for interval. """

        if 'year' in self.args['interval']:
            self.base_query = self.base_query.\
                              group_by(func.year(table.date))

        elif 'month' in self.args['interval']:
            self.base_query = self.base_query.\
                              group_by(func.year(table.date),
                                       func.month(table.date))

        elif 'day' in self.args['interval']:
            self.base_query = self.base_query.\
                              group_by(func.year(table.date),
                                       func.month(table.date),
                                       func.day(table.date))

        elif 'hour' in self.args['interval']:
            self.base_query = self.base_query.\
                              group_by(func.year(table.date),
                                       func.month(table.date),
                                       func.day(table.date),
                                       func.hour(table.date))

        self.base_query = self.base_query.order_by(table.date)

        return self.base_query

    def set_args(self, args):
        """ Return dict with parameters included in GET. """

        interval = self.validate_interval(args.get('interval'),
                                          self.valid_intervals)

        start = args.get('start', None)
        if start is not None:
            try:
                start = moment.date(start)
            except ValueError:
                start = None

        end = args.get('end', None)
        if end is None:
            end = self.set_end(start, args.get('duration', None))
        else:
            end = moment.date(end)

        circuit = args.get('circuit', 'summary')

        base = args.get('base', '65')

        location = args.get('location', '0')

        return {'interval': interval,
                'start': start,
                'end': end,
                'circuit': circuit,
                'base': base,
                'location': location}

    @classmethod
    def validate_interval(cls, interval, valid_options):
        """ Return valid interval option. Remove pluralized versions if any. """

        if interval is not None:
            for option in valid_options:
                if option in interval:
                    return option
        return 'error'

    def set_end(self, start, duration):
        """ Return end date based on duration. """

        if duration is not None:
            # access with duration.group(1) and duration.group(2)
            duration = self.regex.match(duration)
            try:
                end = self.add_duration(start,
                                        duration.group(1),
                                        duration.group(2))
            except AttributeError:
                return None
                #return jsonify( error = 'Duration attibute may lack number or interval. ex. 5months, 1year, 15days')
        else:
            return None

        return end

    @classmethod
    def add_duration(cls, start, duration, interval):
        """ Return end date based on start, duraction (n) and interval. """

        if 'day' in interval:
            return start.clone().add(days=int(duration)).add(minutes=-1)
        elif 'month' in interval:
            return start.clone().add(months=int(duration)).add(minutes=-1)
        elif 'year' in interval:
            return start.clone().add(years=int(duration)).add(minutes=-1)

class ViewSummary(View):
    """ Summary view query and response methods. """

    def __init__(self, args, house_id):
        super(ViewSummary, self).__init__(args)
        if self.success:
            # default to monthly, has more data for 2012
            energy_table = EnergyMonthly
            hdd_table = HDDMonthly
            div = 1

            if 'day' in self.args['interval']:
                energy_table = EnergyHourly
                hdd_table = HDDHourly
                div = 1000

            self.base_query = db_session.\
                              query(energy_table.date,
                                    label('sum_solar', func.sum(energy_table.solar)/div),
                                    label('sum_used', func.sum(energy_table.used)/div),
                                    label('sum_adjusted_load', func.sum(energy_table.adjusted_load)/div),
                                    label('sum_hdd', func.sum(hdd_table.hdd))).\
                outerjoin(hdd_table, and_(energy_table.date == hdd_table.date,
                                            energy_table.house_id == hdd_table.house_id)).\
                filter(energy_table.house_id == house_id) 
    
            self.get_totals(energy_table)
            self.get_items(energy_table)

    def get_totals(self, energy_table):
        """ Get and store totals from database. """

        self.filter_query_by_date_range(energy_table)

        totals = self.base_query.one()

        self.json_totals = {'net': totals.sum_adjusted_load,
                            'solar': totals.sum_solar,
                            'used': totals.sum_used,
                            'hdd': totals.sum_hdd
                           }

    def get_items(self, energy_table):
        """ Get and store rows from database. """

        items = self.group_query_by_interval(energy_table)

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'net': item.sum_adjusted_load,
                    'solar': item.sum_solar,
                    'used': item.sum_used,
                    'hdd': item.sum_hdd}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        if 'year' in self.args['interval']:
            return jsonify(view='summary',
                           totals=self.json_totals,
                           years=self.json_items)

        if 'month' in self.args['interval']:
            return jsonify(view='summary',
                           totals=self.json_totals,
                           months=self.json_items)

        if 'day' in self.args['interval']:
            return jsonify(view='summary',
                           totals=self.json_totals,
                           days=self.json_items)

class ViewGeneration(View):
    """ Genration view query and response methods. """

    def __init__(self, args, house_id):
        super(ViewGeneration, self).__init__(args)

        if self.success:
            self.get_fields(house_id)
            self.get_totals(house_id)
            self.get_items()

    def get_fields(self, house_id):
        """ Get and store additional generation fields from database. """

        tables = [EnergyHourly, EnergyDaily]
        self.max_solar = []
        for table in tables:
            self.base_query = db_session.query(label('max_solar',
                                                     func.min(table.solar))).\
                filter(table.house_id == house_id) # nested query

            sub_query = self.filter_query_by_date_range(table)

            max_solar_query = db_session.query(table.date,
                                               label('max_solar', table.solar)).\
                filter(table.solar == sub_query).one()

            self.max_solar.append({'date': str(max_solar_query.date),
                                   'solar': max_solar_query.max_solar})

    def get_totals(self, house_id):
        """ Get and store totals from database. """

        self.base_query = db_session.query(EnergyMonthly.date,
                                           label('sum_actual',
                                                 func.sum(EnergyMonthly.solar)),
                                           label('sum_estimated',
                                                 func.sum(EstimatedMonthly.solar))).\
            outerjoin(EstimatedMonthly,
                      and_(EnergyMonthly.date == EstimatedMonthly.date,
                           EnergyMonthly.house_id == EstimatedMonthly.house_id)).\
            filter(EnergyMonthly.house_id == house_id)

        self.filter_query_by_date_range(EnergyMonthly)

        totals = self.base_query.one()

        self.json_totals = {'actual': totals.sum_actual,
                            'estimated': totals.sum_estimated}

    def get_items(self):
        """ Get and store rows from database. """

        items = self.group_query_by_interval(EnergyMonthly)

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'actual': item.sum_actual,
                    'estimated': item.sum_estimated}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        if 'year' in self.args['interval']:
            return jsonify(view='generation',
                           max_solar_hour=self.max_solar[0],
                           max_solar_day=self.max_solar[1],
                           totals=self.json_totals,
                           years=self.json_items)

        if 'month' in self.args['interval']:
            return jsonify(view='generation',
                           max_solar_hour=self.max_solar[0],
                           max_solar_day=self.max_solar[1],
                           totals=self.json_totals,
                           months=self.json_items)

class ViewHdd(View):
    """ Hdd view query and response methods. """

    def __init__(self, args, house_id):
        super(ViewHdd, self).__init__(args)
        if self.success:
            self.get_heating_season(house_id)
            self.get_coldest_hour(house_id)
            self.get_coldest_day(house_id)
            self.get_iga(house_id)
            self.get_totals(house_id)
            self.get_items()

    def get_heating_season(self, house_id):
        """ Set base query for heating season. """

        self.base_query = db_session.query(label('total_ashp',
                                                 func.sum(EnergyDaily.ashp)),
                                           label('total_hdd',
                                                 func.sum(HDDDaily.hdd))).\
            filter(EnergyDaily.date == HDDDaily.date).\
            filter(EnergyDaily.house_id == house_id).\
            filter(EnergyDaily.ashp != None)

        self.filter_query_by_date_range(EnergyDaily)

        self.total_hdd_and_ashp_in_heating_season_query = \
            self.filter_query_remove_summer_months(EnergyDaily).one()

    def get_coldest_hour(self, house_id):
        """ Get and store dict of coldest hour from database. """

        self.base_query = db_session.query(label('temperature',
                                                 func.min(TemperatureHourly.temperature))).\
            filter(TemperatureHourly.house_id == house_id).\
            filter(TemperatureHourly.device_id == 0) # outdoor device_id = 0

        sub_query = self.filter_query_by_date_range(TemperatureHourly)

        min_temperature_hour_query = db_session.query(TemperatureHourly.date,
                                                      TemperatureHourly.temperature).\
            filter(TemperatureHourly.temperature == sub_query).first()

        self.json_coldest_hour = {'date': str(min_temperature_hour_query.date),
                                  'temperature': min_temperature_hour_query.temperature}

    def get_coldest_day(self, house_id):
        """ Get and store dict of coldest day from database. """

        self.base_query = db_session.query(label('hdd', func.max(HDDDaily.hdd))).\
            filter(HDDDaily.house_id == house_id)

        sub_query = self.filter_query_by_date_range(HDDDaily)

        min_hdd_day_query = db_session.query(HDDDaily.date, HDDDaily.hdd).\
            filter(HDDDaily.hdd == sub_query).one()

        self.json_coldest_day = {'date': str(min_hdd_day_query.date),
                                 'temperature': min_hdd_day_query.hdd}
        # actually hdd, not temperature. Need to fix here, and in frontend

    def get_iga(self, house_id):
        """ Get and store internal gross area value. """

        self.iga_query = db_session.query(Houses).\
            filter(Houses.house_id == house_id).one()

    def get_totals(self, house_id):
        """ Get and store totals from database. """

        self.base_query = db_session.\
                          query(HDDMonthly.date,
                                label('sum_actual',
                                      func.sum(HDDMonthly.hdd)),
                                label('sum_estimated',
                                      func.sum(EstimatedMonthly.hdd))).\
            outerjoin(EstimatedMonthly, and_(HDDMonthly.date == EstimatedMonthly.date,
                                              HDDMonthly.house_id == EstimatedMonthly.house_id)).\
            filter(HDDMonthly.house_id == house_id)

        self.filter_query_by_date_range(HDDMonthly)

        totals = self.base_query.one()

        self.json_totals = {'actual': totals.sum_actual,
                            'estimated': totals.sum_estimated,
                            'ashp_heating_season': self.total_hdd_and_ashp_in_heating_season_query.total_ashp,
                            'hdd_heating_season': self.total_hdd_and_ashp_in_heating_season_query.total_hdd}

    def get_items(self):
        """ Get and store rows from database. """

        items = self.group_query_by_interval(HDDMonthly)

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'actual': item.sum_actual,
                    'estimated': item.sum_estimated}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        if 'year' in self.args['interval']:
            return jsonify(view='hdd',
                           coldest_hour=self.json_coldest_hour,
                           coldest_day=self.json_coldest_day,
                           iga=self.iga_query.iga,
                           totals=self.json_totals,
                           years=self.json_items)

        if 'month' in self.args['interval']:
            return jsonify(view='hdd',
                           coldest_hour=self.json_coldest_hour,
                           coldest_day=self.json_coldest_day,
                           iga=self.iga_query.iga,
                           totals=self.json_totals,
                           months=self.json_items)

class ViewTemperature(View):
    """ Temperature view query and response methods. """

    def __init__(self, args, house_id):
        super(ViewTemperature, self).__init__(args)
        if self.success:
            self.get_totals(house_id)
            self.get_items()

    def get_totals(self, house_id):
        """ Get and store totals from database. """

        self.base_query = db_session.\
                          query(TemperatureHourly.date,
                                label('min_temperature',
                                      func.min(TemperatureHourly.temperature)),
                                label('max_temperature',
                                      func.max(TemperatureHourly.temperature)),
                                label('avg_temperature',
                                      func.avg(TemperatureHourly.temperature)),
                                label('sum_hdd',
                                      func.sum(HDDHourly.hdd))).\
            outerjoin(HDDHourly, and_(HDDHourly.date == TemperatureHourly.date,
                                      HDDHourly.house_id == TemperatureHourly.house_id)).\
            filter(and_(TemperatureHourly.house_id == house_id,
                        TemperatureHourly.device_id == self.args['location']))

        self.filter_query_by_date_range(TemperatureHourly)

        totals = self.base_query.one()

        self.json_totals = {'min_temperature': totals.min_temperature,
                            'max_temperature': totals.max_temperature,
                            'avg_temperature': totals.avg_temperature,
                            'sum_hdd': totals.sum_hdd}

    def get_items(self):
        """ Get and store rows from database. """

        items = self.group_query_by_interval(TemperatureHourly)

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'min_temperature': item.min_temperature,
                    'max_temperature': item.max_temperature,
                    'avg_temperature': item.avg_temperature,
                    'sum_hdd': item.sum_hdd}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        if 'year' in self.args['interval']:
            return jsonify(view='temperature',
                           totals=self.json_totals,
                           years=self.json_items)

        if 'month' in self.args['interval']:
            return jsonify(view='temperature',
                           totals=self.json_totals,
                           months=self.json_items)

        if 'day' in self.args['interval']:
            return jsonify(view='temperature',
                           totals=self.json_totals,
                           days=self.json_items)

        if 'hour' in self.args['interval']:
            return jsonify(view='temperature',
                           totals=self.json_totals,
                           hours=self.json_items)

class ViewWater(View):
    """ Water view query and response methods. """

    def __init__(self, args, house_id):
        super(ViewWater, self).__init__(args)
        if self.success:
            self.get_totals(house_id)
            self.get_items(house_id)

    def get_totals(self, house_id):
        """ Get and store totals from database. """

        totals = db_session.query("cold", "hot", "main",
                                  "water_heater", "water_pump")

        if self.args['start'] is not None and self.args['end'] is not None:
            date_range = " AND e.date BETWEEN :start AND :end "

        elif self.args['start'] is not None:
            date_range = " AND e.date >= :start "

        elif self.args['end'] is not None:
            date_range = " AND e.date < :end "

        elif self.args['start'] is None and self.args['end'] is None:
            date_range = ""

        sql = """SELECT SUM(main.gallons) - SUM(hot.gallons) AS 'cold',
                    SUM(hot.gallons) AS 'hot', SUM(main.gallons) AS 'main',
                    SUM(e.water_heater) AS 'water_heater',
                    SUM(e.water_pump) AS 'water_pump' 
                 FROM energy_monthly e 
                 LEFT JOIN (SELECT house_id, date, gallons FROM water_monthly
                    WHERE device_id = 6) main ON e.date = main.date
                     AND main.house_id = e.house_id 
                 LEFT JOIN (SELECT house_id, date, gallons FROM water_monthly
                    WHERE device_id = 7) hot ON e.date = hot.date
                      AND hot.house_id = e.house_id
                 WHERE e.house_id = :house_id
                 %s
             """ % date_range

        totals = totals.from_statement(text(sql))
        totals = totals.params(house_id=house_id,
                               start=self.args['start'],
                               end=self.args['end']).one()

        self.json_totals = {'cold': totals.cold,
                            'hot': totals.hot,
                            'main': totals.main,
                            'water_heater':  totals.water_heater,
                            'water_pump': totals.water_pump}

    def get_items(self, house_id):
        """ Get and store rows from database. """

        items = db_session.query("date", "cold", "hot", "main",
                                 "water_heater", "water_pump")

        if self.args['start'] is not None and self.args['end'] is not None:
            date_range = " AND (e.date BETWEEN :start AND :end) "

        elif self.args['start'] is not None:
            date_range = " AND e.date >= :start "

        elif self.args['end'] is not None:
            date_range = " AND e.date < :end "

        elif self.args['start'] is None and self.args['end'] is None:
            date_range = ""

        if 'month' in self.args['interval']:
            grp = ", MONTH(e.date) "

        else:
            grp = ""

        sql = """SELECT e.date AS 'date', SUM(main.gallons) -
                    SUM(hot.gallons) AS 'cold', SUM(hot.gallons) AS 'hot',
                    SUM(main.gallons) AS 'main',
                    SUM(e.water_heater) AS 'water_heater',
                    SUM(e.water_pump) AS 'water_pump' 
                 FROM energy_monthly e 
                 LEFT JOIN (SELECT house_id, date, gallons FROM water_monthly
                    WHERE device_id = 6) main ON e.date = main.date
                        AND main.house_id = e.house_id 
                 LEFT JOIN (SELECT house_id, date, gallons FROM water_monthly
                    WHERE device_id = 7) hot ON e.date = hot.date
                        AND hot.house_id = e.house_id
                 WHERE e.house_id = :house_id
                 %s
                 GROUP BY YEAR(e.date) %s
                 ORDER BY e.date
             """ % (date_range, grp)

        items = items.from_statement(text(sql))
        items = items.params(house_id=house_id,
                             start=self.args['start'],
                             end=self.args['end']).all()

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'cold': item.cold,
                    'hot': item.hot,
                    'main': item.main,
                    'water_heater':  item.water_heater,
                    'water_pump': item.water_pump}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        if 'year' in self.args['interval']:
            return jsonify(view='water',
                           totals=self.json_totals,
                           years=self.json_items)

        if 'month' in self.args['interval']:
            return jsonify(view='water',
                           totals=self.json_totals,
                           months=self.json_items)

class ViewBasetemp(View):
    """ Basetemp analysis view query and response methods. """

    def __init__(self, args, house_id):

        super(ViewBasetemp, self).__init__(args)
        if self.success:
            self.get_items(house_id)

    def get_items(self, house_id):
        """ Get and store points (primarily hdd and ashp values) from database. """

        items = db_session.query("hdd", "ashp", "temperature", "date", "solar")

        if self.args['start'] is not None and self.args['end'] is not None:
            date_range = " date BETWEEN :start AND :end "

        elif self.args['start'] is not None:
            date_range = " date >= :start "

        elif self.args['end'] is not None:
            date_range = " date < :end "

        if self.args['interval'] == 'hour':
            sql = "SELECT e.date AS 'date', t.hdd AS 'hdd', e.ashp/1000.0 AS 'ashp', t.temperature AS 'temperature', e.solar/1000.0 AS 'solar' "

        else:
            sql = "SELECT e.date AS 'date', SUM(t.hdd) AS 'hdd', SUM(e.ashp)/1000.0 AS 'ashp', AVG(t.temperature) AS 'temperature', SUM(e.solar)/1000.0 AS 'solar' "

        sql = sql + \
        """FROM (SELECT date, solar, ashp FROM energy_hourly WHERE house_id = :house_id AND solar > -500 AND ashp > 0 AND %s) e
           LEFT JOIN (SELECT date, temperature, (:base - temperature) / 24.0 AS 'hdd' FROM temperature_hourly
           WHERE house_id = :house_id AND device_id = 0 AND temperature <= :base AND %s) t ON e.date = t.date
           WHERE t.date = e.date
        """ % (date_range, date_range)

        if self.args['interval'] == 'month':
            sql = sql + "GROUP BY YEAR(t.date), MONTH(t.date)"

        if self.args['interval'] == 'day':
            sql = sql + "GROUP BY CAST(t.date AS DATE)"

        items = items.from_statement(text(sql))
        items = items.params(house_id=house_id,
                             base=self.args['base'],
                             start=self.args['start'],
                             end=self.args['end']).all()

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'solar': item.solar,
                    'ashp': item.ashp,
                    'temperature': item.temperature,
                    'hdd': item.hdd}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """
        if not self.success:
            return jsonify(self.error)

        return jsonify(view='heat',
                       base=self.args['base'],
                       interval=self.args['interval'],
                       points=self.json_items)

class ViewUsage(View):
    """ Usage view queries and response methods. """

    def __init__(self, args, house_id):

        super(ViewUsage, self).__init__(args)

        if self.success:

            self.circuits = CircuitDict(house_id)
    
            if self.args['circuit'] == 'summary':
                self.get_summary(house_id)
    
            elif self.args['circuit'] == 'all':
                self.get_circuit_all(house_id)
    
            elif self.args['circuit'] == 'ashp':
                self.get_circuit_ashp(house_id)
    
            elif self.args['circuit'] == 'all_other':
                self.get_circuit_all_other(house_id)
    
            else:
                self.get_circuit_x(house_id, self.args['circuit'])

    def get_summary(self, house_id):
        """ Get and store summary usage values from database. """

        self.base_query = db_session.query(label('used',
                                                 func.sum(EnergyDaily.used)),
                                           label('water_heater',
                                                 func.sum(EnergyDaily.water_heater)),
                                           label('ashp',
                                                 func.sum(EnergyDaily.ashp)),
                                           label('water_pump',
                                                 func.sum(EnergyDaily.water_pump)),
                                           label('dryer',
                                                 func.sum(EnergyDaily.dryer)),
                                           label('washer',
                                                 func.sum(EnergyDaily.washer)),
                                           label('dishwasher',
                                                 func.sum(EnergyDaily.dishwasher)),
                                           label('stove',
                                                 func.sum(EnergyDaily.stove)),
                                           label('refrigerator',
                                                 func.sum(EnergyDaily.refrigerator)),
                                           label('living_room',
                                                 func.sum(EnergyDaily.living_room)),
                                           label('aux_heat_bedrooms',
                                                 func.sum(EnergyDaily.aux_heat_bedrooms)),
                                           label('aux_heat_living',
                                                 func.sum(EnergyDaily.aux_heat_living)),
                                           label('study',
                                                 func.sum(EnergyDaily.study)),
                                           label('barn',
                                                 func.sum(EnergyDaily.barn)),
                                           label('basement_west',
                                                 func.sum(EnergyDaily.basement_west)),
                                           label('basement_east',
                                                 func.sum(EnergyDaily.basement_east)),
                                           label('ventilation',
                                                 func.sum(EnergyDaily.ventilation)),
                                           label('ventilation_preheat',
                                                 func.sum(EnergyDaily.ventilation_preheat)),
                                           label('kitchen_recept_rt',
                                                 func.sum(EnergyDaily.kitchen_recept_rt))).\
            filter(EnergyDaily.house_id == house_id).\
            filter(or_(EnergyDaily.device_id == 5,
                       EnergyDaily.device_id == 10))

        self.filter_query_by_date_range(EnergyDaily)

        totals = self.base_query.one()

        self.json_circuits = []
        subtotal = 0
        for column in self.base_query.column_descriptions:
            actual = getattr(totals, column['name'])
            if actual is None:
                actual = 0
            if column['name'] == 'used':
                subtotal = subtotal + actual
            else:
                subtotal = subtotal - actual

            self.json_circuits.append({'circuit_id': column['name'],
                                       'actual': actual,
                                       'name': self.get_circuit_info(column['name'])['name']
                                      })
        self.json_circuits.append({'circuit_id': 'all_other',
                                   'actual': subtotal,
                                   'name': self.get_circuit_info('all_other')['name']
                                  })
        self.json_circuit = {'circuit_id': 'summary',
                             'name':  'Total'}

    def get_circuit_all(self, house_id):
        """ Get and store all circuit usage total and by interval from database. """

        self.base_query = db_session.query(label('date',
                                                 EnergyMonthly.date),
                                           label('actual',
                                                 func.sum(EnergyMonthly.used)),
                                           label('budget',
                                                 func.sum(EstimatedMonthly.used))
                                          ). \
            join(EstimatedMonthly, and_(EnergyMonthly.date == EstimatedMonthly.date,
                                         EnergyMonthly.house_id == EstimatedMonthly.house_id)).\
            filter(EnergyMonthly.house_id == house_id)

        self.filter_query_by_date_range(EnergyMonthly)

        totals = self.base_query.one()

        self.json_totals = {'actual': totals.actual,
                            'budget': totals.budget}

        items = self.group_query_by_interval(EnergyMonthly)

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'actual': item.actual,
                    'budget': item.budget}
            self.json_items.append(data)

        self.json_circuit = {'circuit_id': 'all',
                             'name':  self.get_circuit_info('all')['name'],
                             'description': self.get_circuit_info('all')['description']}

    def get_circuit_ashp(self, house_id):
        """ Get and store ashp usage total and by interval from database. """

        session = db_session.query("date", "actual", "hdd")

        if self.args['start'] is not None and self.args['end'] is not None:
            date_range = " AND (date BETWEEN :start AND :end) "

        elif self.args['start'] is not None:
            date_range = " AND date >= :start "

        elif self.args['end'] is not None:
            date_range = " AND date < :end "

        elif self.args['start'] is None and self.args['end'] is None:
            date_range = ""

        sql = """SELECT e.date AS 'date', SUM(e.ashp) AS 'actual', SUM(t.hdd) AS 'hdd'
                 FROM 
                    (SELECT date, SUM( IF( ((:base - temperature) / 24) > 0,
                        ((:base - temperature) / 24), 0) ) AS 'hdd' 
                    FROM temperature_hourly
                    WHERE house_id = :house_id
                        AND device_id = 0 
                        %s
                    GROUP BY MONTH(date), DAY(date) ) t,
                    (SELECT date, ashp
                    FROM energy_daily 
                    WHERE house_id = :house_id
                        %s
                        AND (device_id = 5 OR device_id = 10) ) e
                WHERE t.date = e.date
            """ % (date_range, date_range)

        totals = session.from_statement(text(sql))
        totals = totals.params(house_id=house_id,
                               start=self.args['start'],
                               end=self.args['end'],
                               base=self.args['base']).one()

        self.json_totals = {'actual': totals.actual,
                            'hdd': totals.hdd}

        if self.args['start'] is not None and self.args['end'] is not None:
            date_range = "date BETWEEN :start AND :end "
            date_range_t = "AND t." + date_range
            date_range = "AND " + date_range

        elif self.args['start'] is not None:
            date_range = "date >= :start "
            date_range_t = "AND t." + date_range
            date_range = "AND " + date_range

        elif self.args['end'] is not None:
            date_range = "date < :end "
            date_range_t = "AND t." + date_range
            date_range = "AND " + date_range

        elif self.args['start'] is None and self.args['end'] is None:
            date_range = ""
            date_range_t = ""

        if 'month' in self.args['interval']:
            grp = ", MONTH(e.date) "

        else:
            grp = ""

        sql = """SELECT e.date AS 'date', e.ashp AS 'actual',
                    SUM( IF( ((:base - t.temperature) / 24) > 0,
                    ((:base - t.temperature) / 24), 0) ) AS 'hdd' 
                 FROM temperature_hourly t, 
                    (SELECT date, ashp FROM energy_monthly
                     WHERE house_id = :house_id
                     %s
                     AND (device_id = 5 OR device_id = 10)) e
                 WHERE t.device_id = 0
                    AND t.house_id = :house_id
                    %s
                    AND MONTH(e.date) = MONTH(t.date)
                 GROUP BY YEAR(e.date) %s
             """ % (date_range, date_range_t, grp)

        items = session.from_statement(text(sql))
        items = items.params(house_id=house_id,
                             start=self.args['start'],
                             end=self.args['end'],
                             base=self.args['base']).all()

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'actual': item.actual,
                    'hdd': item.hdd}
            self.json_items.append(data)

        self.json_circuit = {'circuit_id': 'ashp',
                             'name':  self.get_circuit_info('ashp')['name'],
                             'description': self.get_circuit_info('ashp')['description']}

    def get_circuit_all_other(self, house_id):
        """ Get and store all other unmonitored circuits total and by interval from database. """

        self.base_query = db_session.\
                          query(label('date', EnergyDaily.date),
                                label('actual',
                                      func.sum(EnergyDaily.used) -
                                      func.sum(func.IF(EnergyDaily.water_heater != None,
                                                       EnergyDaily.water_heater, 0)) -
                                      func.sum(func.IF(EnergyDaily.ashp != None,
                                                       EnergyDaily.ashp, 0)) -
                                      func.sum(func.IF(EnergyDaily.water_pump != None,
                                                       EnergyDaily.water_pump, 0)) -
                                      func.sum(func.IF(EnergyDaily.dryer != None,
                                                       EnergyDaily.dryer, 0)) -
                                      func.sum(func.IF(EnergyDaily.washer != None,
                                                       EnergyDaily.washer, 0)) -
                                      func.sum(func.IF(EnergyDaily.dishwasher != None,
                                                       EnergyDaily.dishwasher, 0)) -
                                      func.sum(func.IF(EnergyDaily.stove != None,
                                                       EnergyDaily.stove, 0)) -
                                      func.sum(func.IF(EnergyDaily.refrigerator != None,
                                                       EnergyDaily.refrigerator, 0)) -
                                      func.sum(func.IF(EnergyDaily.living_room != None,
                                                       EnergyDaily.living_room, 0)) -
                                      func.sum(func.IF(EnergyDaily.aux_heat_bedrooms != None,
                                                       EnergyDaily.aux_heat_bedrooms, 0)) -
                                      func.sum(func.IF(EnergyDaily.aux_heat_living != None,
                                                       EnergyDaily.aux_heat_living, 0)) -
                                      func.sum(func.IF(EnergyDaily.study != None,
                                                       EnergyDaily.study, 0)) -
                                      func.sum(func.IF(EnergyDaily.barn != None,
                                                       EnergyDaily.barn, 0)) -
                                      func.sum(func.IF(EnergyDaily.basement_west != None,
                                                       EnergyDaily.basement_west, 0)) -
                                      func.sum(func.IF(EnergyDaily.basement_east != None,
                                                       EnergyDaily.basement_east, 0)) -
                                      func.sum(func.IF(EnergyDaily.ventilation != None,
                                                       EnergyDaily.ventilation, 0)) -
                                      func.sum(func.IF(EnergyDaily.ventilation_preheat != None,
                                                       EnergyDaily.ventilation_preheat, 0)) -
                                      func.sum(func.IF(EnergyDaily.kitchen_recept_rt != None, \
                                                       EnergyDaily.kitchen_recept_rt, 0)))).\
            filter(EnergyDaily.house_id == house_id).\
            filter(or_(EnergyDaily.device_id == 5,
                       EnergyDaily.device_id == 10))

        self.filter_query_by_date_range(EnergyDaily)

        totals = self.base_query.one()

        self.json_totals = {'actual': totals.actual}

        items = self.group_query_by_interval(EnergyDaily)

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'actual': item.actual}
            self.json_items.append(data)

        self.json_circuit = {'circuit_id': 'all_other',
                             'name':  self.get_circuit_info('all_other')['name'],
                             'description': self.get_circuit_info('all_other')['description']}

    def get_circuit_x(self, house_id, circuit):
        """ Get and store circuit x total and by interval from database. """

        self.base_query = db_session.\
                          query(label('date', EnergyDaily.date),
                                label('actual',
                                      func.sum(getattr(EnergyDaily, circuit)))
                               ).\
            filter(EnergyDaily.house_id == house_id).\
            filter(or_(EnergyDaily.device_id == 5,
                       EnergyDaily.device_id == 10))

        self.filter_query_by_date_range(EnergyDaily)

        totals = self.base_query.one()

        self.json_totals = {'actual': totals.actual}

        items = self.group_query_by_interval(EnergyDaily)

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'actual': item.actual}
            self.json_items.append(data)

        self.json_circuit = {'circuit_id': circuit,
                             'name':  self.get_circuit_info(circuit)['name'],
                             'description': self.get_circuit_info(circuit)['description']}

    def get_circuit_info(self, circuit_id):
        """ Return circuit details as dict. """

        for row in self.circuits.circuits:

            if row.circuit_id == circuit_id:

                return {'name': row.name,
                        'description': row.description}

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        if self.args['circuit'] == 'summary':

            return jsonify(view='usage.summary',
                           circuits=self.json_circuits,
                           circuit=self.json_circuit)

        elif self.args['circuit'] == 'all':

            return jsonify(view='usage.all',
                           interval=self.args['interval'],
                           circuit=self.json_circuit,
                           totals=self.json_totals,
                           months=self.json_items)

        elif self.args['circuit'] == 'ashp':

            return jsonify(view='usage.ashp',
                           interval=self.args['interval'],
                           circuit=self.json_circuit,
                           totals=self.json_totals,
                           months=self.json_items)

        elif self.args['circuit'] == 'all_other':

            return jsonify(view='usage.all_other',
                           interval=self.args['interval'],
                           circuit=self.json_circuit,
                           totals=self.json_totals,
                           months=self.json_items)

        else:
            # all other circuits
            return jsonify(view='usage.' + self.args['circuit'],
                           interval=self.args['interval'],
                           circuit=self.json_circuit,
                           totals=self.json_totals,
                           months=self.json_items)

class ViewChart(View):
    """ Hourly chart view query and response methods. """

    def __init__(self, args, house_id):

        super(ViewChart, self).__init__(args)

        if self.success:
            self.get_items(house_id)

    def get_items(self, house_id):
        """ Get and store hourly values from database. """

        items = db_session.query("date", "net", "solar", "used",
                                 "first_floor_temp", "second_floor_temp",
                                 "basement_temp", "outdoor_temp", "hdd",
                                 "water_heater", "ashp", "water_pump",
                                 "dryer", "washer", "dishwasher", "stove",
                                 "refrigerator", "living_room",
                                 "aux_heat_bedrooms", "aux_heat_living",
                                 "study", "barn", "basement_west",
                                 "basement_east", "ventilation",
                                 "ventilation_preheat", "kitchen_recept_rt",
                                 "all_other")

        sql = """SELECT ti1.date AS 'date', e.adjusted_load AS 'net',
          e.solar AS 'solar', e.used AS 'used',
          ti1.indoor1_deg AS 'first_floor_temp',
          ti2.indoor2_deg AS 'second_floor_temp',
          ti0.indoor0_deg AS 'basement_temp', 
          tu.outdoor_deg AS 'outdoor_temp', th.hdd AS 'hdd',
          e.water_heater AS 'water_heater', e.ashp AS 'ashp',
          e.water_pump AS 'water_pump', e.dryer AS 'dryer',
          e.washer AS 'washer', e.dishwasher AS 'dishwasher',
          e.stove AS 'stove', e.refrigerator AS 'refrigerator',
          e.living_room AS 'living_room',
          e.aux_heat_bedrooms AS 'aux_heat_bedrooms',
          e.aux_heat_living AS 'aux_heat_living', e.study AS 'study',
          e.barn AS 'barn', e.basement_west AS 'basement_west',
          e.basement_east AS 'basement_east', e.ventilation AS 'ventilation',
          e.ventilation_preheat AS 'ventilation_preheat',
          e.kitchen_recept_rt AS 'kitchen_recept_rt',
          e.used-(e.water_heater + e.ashp + e.water_pump + e.dryer +
          e.washer + e.dishwasher + e.stove + e.refrigerator + e.living_room +
          e.aux_heat_bedrooms + e.aux_heat_living + e.study + e.barn +
          e.basement_west + e.basement_east + e.ventilation +
          e.ventilation_preheat + e.kitchen_recept_rt) AS 'all_other'
        FROM (SELECT house_id, date, temperature AS 'indoor1_deg'
              FROM temperature_hourly
              WHERE device_id = 1) ti1
          LEFT JOIN (SELECT house_id, date, temperature AS 'indoor2_deg'
                     FROM temperature_hourly WHERE device_id = 2) ti2 
            ON CAST(LEFT(ti2.date,13) AS DATETIME) = CAST(LEFT(ti1.date,13) AS DATETIME)
                AND ti2.house_id = ti1.house_id
          LEFT JOIN (SELECT house_id, date, temperature AS 'indoor0_deg'
                     FROM temperature_hourly WHERE device_id = 3) ti0 
            ON CAST(LEFT(ti0.date,13) AS DATETIME) = CAST(LEFT(ti1.date,13) AS DATETIME)
                AND ti0.house_id = ti1.house_id
          LEFT JOIN (SELECT house_id, date, temperature AS 'outdoor_deg'
                     FROM temperature_hourly WHERE device_id = 0) tu 
            ON CAST(LEFT(tu.date,13) AS DATETIME) = CAST(LEFT(ti1.date,13) AS DATETIME)
                AND tu.house_id = ti1.house_id
          LEFT JOIN (SELECT house_id, date, hdd
                     FROM hdd_hourly) th 
            ON CAST(LEFT(th.date,13) AS DATETIME) = CAST(LEFT(ti1.date,13) AS DATETIME)
                AND th.house_id = ti1.house_id
          LEFT JOIN energy_hourly e 
            ON CAST(LEFT(e.date,13) AS DATETIME) = CAST(LEFT(ti1.date,13) AS DATETIME)
                AND e.house_id = ti1.house_id
        WHERE CAST(ti1.date AS DATE) = DATE(:start)
          AND ti1.house_id = :house_id
        ORDER BY e.date
        """

        items = items.from_statement(text(sql))
        items = items.params(house_id=house_id,
                             start=self.args['start'],
                             end=self.args['end']).all()

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'net': item.net,
                    'solar': item.solar,
                    'used': item.used,
                    'first_floor_temp': item.first_floor_temp,
                    'second_floor_temp': item.second_floor_temp,
                    'basement_temp': item.basement_temp,
                    'outdoor_temp': item.outdoor_temp,
                    'hdd': item.hdd,
                    'water_heater': item.water_heater,
                    'ashp': item.ashp,
                    'water_pump':item.water_pump,
                    'dryer': item.dryer,
                    'washer': item.washer,
                    'dishwasher': item.dishwasher,
                    'stove': item.stove,
                    'refrigerator': item.refrigerator,
                    'living_room': item.living_room,
                    'aux_heat_bedrooms': item.aux_heat_bedrooms,
                    'aux_heat_living': item.aux_heat_living,
                    'study': item.study,
                    'barn': item.barn,
                    'basement_west': item.basement_west,
                    'basement_east': item.basement_east,
                    'ventilation': item.ventilation,
                    'ventilation_preheat': item.ventilation_preheat,
                    'kitchen_recept_rt': item.kitchen_recept_rt,
                    'all_other': item.all_other}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        return jsonify(view='chart',
                       interval=self.args['interval'],
                       hours=self.json_items)

class ViewHeatmap(View):
    """ Daily heatmap view query and response methods. """

    def __init__(self, args, house_id):

        super(ViewHeatmap, self).__init__(args)

        if self.success:
            self.get_items(house_id)

    def get_items(self, house_id):
        """ Get and store daily values from database. """

        items = db_session.query("date", "net", "solar", "used",
                                 "outdoor_deg_min", "outdoor_deg_max",
                                 "hdd", "water_heater", "ashp",
                                 "water_pump", "dryer", "washer",
                                 "dishwasher", "stove", "refrigerator",
                                 "living_room", "aux_heat_bedrooms",
                                 "aux_heat_living", "study", "barn",
                                 "basement_west", "basement_east",
                                 "ventilation", "ventilation_preheat",
                                 "kitchen_recept_rt", "all_other")

        if self.args['start'] is not None and self.args['end'] is not None:
            date_range = " tu.date BETWEEN :start AND :end "

        elif self.args['start'] is not None:
            date_range = " tu.date >= :start "

        elif self.args['end'] is not None:
            date_range = " tu.date < :end "

        sql = """SELECT tu.date AS 'date', e.adjusted_load AS 'net',
                    e.solar AS 'solar', e.used AS 'used',
                    tu.outdoor_deg_min AS 'outdoor_deg_min',
                    tu.outdoor_deg_max AS 'outdoor_deg_max',  
                    th.hdd AS 'hdd', e.water_heater AS 'water_heater',
                    e.ashp AS 'ashp', e.water_pump AS 'water_pump',
                    e.dryer AS 'dryer', e.washer AS 'washer',
                    e.dishwasher AS 'dishwasher', e.stove AS 'stove',
                    e.refrigerator AS 'refrigerator',
                    e.living_room AS 'living_room',
                    e.aux_heat_bedrooms AS 'aux_heat_bedrooms',
                    e.aux_heat_living AS 'aux_heat_living',
                    e.study AS 'study', e.barn AS 'barn',
                    e.basement_west AS 'basement_west',
                    e.basement_east AS 'basement_east',
                    e.ventilation AS 'ventilation',
                    e.ventilation_preheat AS 'ventilation_preheat',
                    e.kitchen_recept_rt AS 'kitchen_recept_rt',
                    e.used-(e.water_heater + e.ashp + e.water_pump +
                    e.dryer + e.washer + e.dishwasher + e.stove +
                    e.refrigerator + e.living_room +
                    e.aux_heat_bedrooms + e.aux_heat_living + e.study +
                    e.barn + e.basement_west + e.basement_east +
                    e.ventilation + e.ventilation_preheat +
                    e.kitchen_recept_rt) AS 'all_other' 
                 FROM (SELECT house_id, date,
                        temperature_min AS 'outdoor_deg_min',
                        temperature_max AS 'outdoor_deg_max'
                       FROM temperature_daily
                       WHERE device_id = 0) tu 
                    LEFT JOIN (SELECT house_id, date, hdd FROM hdd_daily) th
                        ON th.date = tu.date AND th.house_id = tu.house_id
                    LEFT JOIN energy_daily e ON e.date = tu.date
                        AND e.house_id = tu.house_id
                 WHERE tu.house_id = :house_id
                 AND %s
                 ORDER BY e.date
             """ % date_range

        items = items.from_statement(text(sql))
        items = items.params(house_id=house_id,
                             base=self.args['base'],
                             start=self.args['start'],
                             end=self.args['end']).all()

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'net': item.net,
                    'solar': item.solar,
                    'used': item.used,
                    'outdoor_deg_min': item.outdoor_deg_min,
                    'outdoor_deg_max': item.outdoor_deg_max,
                    'hdd': item.hdd,
                    'water_heater': item.water_heater,
                    'ashp': item.ashp,
                    'water_pump':item.water_pump,
                    'dryer': item.dryer,
                    'washer': item.washer,
                    'dishwasher': item.dishwasher,
                    'stove': item.stove,
                    'refrigerator': item.refrigerator,
                    'living_room': item.living_room,
                    'aux_heat_bedrooms': item.aux_heat_bedrooms,
                    'aux_heat_living': item.aux_heat_living,
                    'study': item.study,
                    'barn': item.barn,
                    'basement_west': item.basement_west,
                    'basement_east': item.basement_east,
                    'ventilation': item.ventilation,
                    'ventilation_preheat': item.ventilation_preheat,
                    'kitchen_recept_rt': item.kitchen_recept_rt,
                    'all_other': item.all_other}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        return jsonify(view='heatmap',
                       interval=self.args['interval'],
                       days=self.json_items)

class CircuitDict(object):
    """ Helper query and response methods. Used for circuits endpoint and in ViewUsage class. """

    def __init__(self, house_id):

        self.circuits = self.get_circuits(house_id)

    def get_circuits(self, house_id):
        """ Get, store and return list of circuits from database. """

        circuits = db_session.query(Circuits). \
            filter(Circuits.house_id == house_id).all()

        self.json_items = []
        for circuit in circuits:
            data = {'circuit_id': circuit.circuit_id,
                    'name': circuit.name,
                    'description': circuit.description}
            self.json_items.append(data)

        return circuits

    def get_response(self):
        """ Return response in json format. """

        return jsonify(circuits=self.json_items)
