""" ViewUsage class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.views.view import View
from chartingperformance.views.circuit import CircuitDict

from chartingperformance.models import EnergyHourly
from chartingperformance.models import EnergyMonthly
from chartingperformance.models import EstimatedMonthly

from flask import jsonify

from sqlalchemy import func
from sqlalchemy.sql import label, and_, or_, text

class Usage(View):
    """ Usage view queries and response methods. """

    def __init__(self, args, house_id):

        super(Usage, self).__init__(args)

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
                                                 func.sum(EnergyHourly.used)/1000),
                                           label('water_heater',
                                                 func.sum(EnergyHourly.water_heater)/1000),
                                           label('ashp',
                                                 func.sum(EnergyHourly.ashp)/1000),
                                           label('water_pump',
                                                 func.sum(EnergyHourly.water_pump)/1000),
                                           label('dryer',
                                                 func.sum(EnergyHourly.dryer)/1000),
                                           label('washer',
                                                 func.sum(EnergyHourly.washer)/1000),
                                           label('dishwasher',
                                                 func.sum(EnergyHourly.dishwasher)/1000),
                                           label('stove',
                                                 func.sum(EnergyHourly.stove)/1000),
                                           label('refrigerator',
                                                 func.sum(EnergyHourly.refrigerator)/1000),
                                           label('living_room',
                                                 func.sum(EnergyHourly.living_room)/1000),
                                           label('aux_heat_bedrooms',
                                                 func.sum(EnergyHourly.aux_heat_bedrooms)/1000),
                                           label('aux_heat_living',
                                                 func.sum(EnergyHourly.aux_heat_living)/1000),
                                           label('study',
                                                 func.sum(EnergyHourly.study)/1000),
                                           label('barn',
                                                 func.sum(EnergyHourly.barn)/1000),
                                           label('basement_west',
                                                 func.sum(EnergyHourly.basement_west)/1000),
                                           label('basement_east',
                                                 func.sum(EnergyHourly.basement_east)/1000),
                                           label('ventilation',
                                                 func.sum(EnergyHourly.ventilation)/1000),
                                           label('ventilation_preheat',
                                                 func.sum(EnergyHourly.ventilation_preheat)/1000),
                                           label('kitchen_recept_rt',
                                                 func.sum(EnergyHourly.kitchen_recept_rt)/1000)).\
            filter(EnergyHourly.house_id == house_id).\
            filter(or_(EnergyHourly.device_id == 5,
                       EnergyHourly.device_id == 10))

        self.filter_query_by_date_range(EnergyHourly)

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
        if 'year' in self.args['interval']:
            self.json_circuit = {'circuit_id': 'summary',
                                 'name':  'Total'}
        else:
            self.json_circuit = {'circuit_id': 'summary',
                                 'startdate': self.args['start'].strftime("%Y-%m-%d"),
                                 'enddate': self.args['end'].strftime("%Y-%m-%d"),
                                 'name':  'Total'}

    def get_circuit_all(self, house_id):
        """ Get and store all circuit usage total and by interval from database. """

        if 'year' in self.args['interval'] or 'month' in self.args['interval']:
            self.get_circuit_all_year_month(house_id)

        elif 'day' in self.args['interval'] or 'hour' in self.args['interval']:
            self.get_circuit_all_day_hour(house_id)

    def get_circuit_all_year_month(self, house_id):
        """ Get and store all circuit usage total for yearly or monthly. """

        self.base_query = db_session.query(label('date',
                                                 EnergyMonthly.date),
                                           label('actual',
                                                 func.sum(EnergyMonthly.used)),
                                           label('budget',
                                                 func.sum(EstimatedMonthly.used))
                                          ). \
            outerjoin(EstimatedMonthly, and_(EnergyMonthly.date == EstimatedMonthly.date,
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

    def get_circuit_all_day_hour(self, house_id):
        """ Get and store all circuit usage total for daily or hourly. """

        self.base_query = db_session.query(label('actual',
                                                 func.sum(EnergyHourly.used)/1000)).\
            filter(EnergyHourly.house_id == house_id)

        if 'hour' in self.args['interval']:
            self.base_query = self.base_query.\
                        add_column(label('date', EnergyHourly.date))
        else:
            self.base_query = self.base_query.\
                        add_column(label('date', func.date(EnergyHourly.date)))

        self.filter_query_by_date_range(EnergyHourly)

        totals = self.base_query.one()

        self.json_totals = {'actual': totals.actual}

        items = self.group_query_by_interval(EnergyHourly)

        self.json_items = []
        for item in items:
            data = {'date': self.format_date(item.date),
                    'actual': item.actual}
            self.json_items.append(data)

        self.json_circuit = {'circuit_id': 'all',
                             'name':  self.get_circuit_info('all')['name'],
                             'description': self.get_circuit_info('all')['description']}

    def get_circuit_ashp(self, house_id):
        """ Get and store ashp usage total and by interval from database. """

        session = db_session.query("date", "actual", "hdd")

        if self.args['start'] is not None and self.args['end'] is not None:
            date_range = " AND (e.date BETWEEN :start AND :end) "

        elif self.args['start'] is not None:
            date_range = " AND e.date >= :start "

        elif self.args['end'] is not None:
            date_range = " AND e.date < :end "

        elif self.args['start'] is None and self.args['end'] is None:
            date_range = ""

        date_column_format = "e.date"

        if self.args['interval'] is not 'hour':
            date_column_format = "DATE(e.date)"

        sql = """SELECT %s AS 'date', SUM(e.ashp)/1000.0 AS 'actual',
                  SUM( IF( ((:base - t.temperature) / 24) > 0,
                  ((:base - t.temperature) / 24), 0) ) AS 'hdd'
                 FROM temperature_hourly t, energy_hourly e
                 WHERE t.device_id = 0
                  AND t.house_id = :house_id
                  AND e.house_id = :house_id
                  AND (e.device_id = 5 OR e.device_id = 10)
                  %s
                  AND e.date = t.date
             """ % (date_column_format, date_range)

        totals = session.from_statement(text(sql))
        totals = totals.params(house_id=house_id,
                               start=self.args['start'],
                               end=self.args['end'],
                               base=self.args['base']).one()

        self.json_totals = {'actual': totals.actual,
                            'hdd': totals.hdd}

        grp = ""

        if 'month' in self.args['interval']:
            grp = ", MONTH(e.date) "

        elif 'day' in self.args['interval']:
            grp = ", MONTH(e.date), DAY(e.date) "

        elif 'hour' in self.args['interval']:
            grp = ", MONTH(e.date), DAY(e.date), HOUR(e.date) "

        sql = sql + " GROUP BY YEAR(e.date)" + grp

        items = session.from_statement(text(sql))
        items = items.params(house_id=house_id,
                             start=self.args['start'],
                             end=self.args['end'],
                             base=self.args['base']).all()

        self.json_items = []
        for item in items:
            data = {'date': self.format_date(item.date),
                    'actual': item.actual,
                    'hdd': item.hdd}
            self.json_items.append(data)

        self.json_circuit = {'circuit_id': 'ashp',
                             'name':  self.get_circuit_info('ashp')['name'],
                             'description': self.get_circuit_info('ashp')['description']}

    def get_circuit_all_other(self, house_id):
        """ Get and store all other unmonitored circuits total and by interval from database. """

        self.base_query = db_session.\
                          query(label('actual',
                                      func.sum(EnergyHourly.used)/1000 -
                                      func.sum(func.IF(EnergyHourly.water_heater != None,
                                                       EnergyHourly.water_heater/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.ashp != None,
                                                       EnergyHourly.ashp/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.water_pump != None,
                                                       EnergyHourly.water_pump/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.dryer != None,
                                                       EnergyHourly.dryer/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.washer != None,
                                                       EnergyHourly.washer/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.dishwasher != None,
                                                       EnergyHourly.dishwasher/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.stove != None,
                                                       EnergyHourly.stove/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.refrigerator != None,
                                                       EnergyHourly.refrigerator/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.living_room != None,
                                                       EnergyHourly.living_room/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.aux_heat_bedrooms != None,
                                                       EnergyHourly.aux_heat_bedrooms/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.aux_heat_living != None,
                                                       EnergyHourly.aux_heat_living/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.study != None,
                                                       EnergyHourly.study/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.barn != None,
                                                       EnergyHourly.barn/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.basement_west != None,
                                                       EnergyHourly.basement_west/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.basement_east != None,
                                                       EnergyHourly.basement_east/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.ventilation != None,
                                                       EnergyHourly.ventilation/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.ventilation_preheat != None,
                                                       EnergyHourly.ventilation_preheat/1000, 0)) -
                                      func.sum(func.IF(EnergyHourly.kitchen_recept_rt != None, \
                                                       EnergyHourly.kitchen_recept_rt/1000, 0)))).\
            filter(EnergyHourly.house_id == house_id).\
            filter(or_(EnergyHourly.device_id == 5,
                       EnergyHourly.device_id == 10))

        if 'hour' in self.args['interval']:
            self.base_query = self.base_query.\
                        add_column(label('date', EnergyHourly.date))
        else:
            self.base_query = self.base_query.\
                        add_column(label('date', func.date(EnergyHourly.date)))

        self.filter_query_by_date_range(EnergyHourly)

        totals = self.base_query.one()

        self.json_totals = {'actual': totals.actual}

        items = self.group_query_by_interval(EnergyHourly)

        self.json_items = []
        for item in items:
            data = {'date': self.format_date(item.date),
                    'actual': item.actual}
            self.json_items.append(data)

        self.json_circuit = {'circuit_id': 'all_other',
                             'name':  self.get_circuit_info('all_other')['name'],
                             'description': self.get_circuit_info('all_other')['description']}

    def get_circuit_x(self, house_id, circuit):
        """ Get and store circuit x total and by interval from database. """

        self.base_query = db_session.\
                          query(label('actual',
                                      func.sum(getattr(EnergyHourly, circuit))/1000)
                               ).\
            filter(EnergyHourly.house_id == house_id).\
            filter(or_(EnergyHourly.device_id == 5,
                       EnergyHourly.device_id == 10))

        if 'hour' in self.args['interval']:
            self.base_query = self.base_query.\
                        add_column(label('date', EnergyHourly.date))
        else:
            self.base_query = self.base_query.\
                        add_column(label('date', func.date(EnergyHourly.date)))

        self.filter_query_by_date_range(EnergyHourly)

        totals = self.base_query.one()

        self.json_totals = {'actual': totals.actual}

        items = self.group_query_by_interval(EnergyHourly)

        self.json_items = []
        for item in items:
            data = {'date': self.format_date(item.date),
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
            return jsonify(view='usage.' + self.args['circuit'],
                           circuits=self.json_circuits,
                           circuit=self.json_circuit)

        return jsonify(view='usage.' + self.args['circuit'],
                       interval=self.args['interval'],
                       circuit=self.json_circuit,
                       totals=self.json_totals,
                       items=self.json_items)
