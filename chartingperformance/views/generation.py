""" ViewGeneration class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.views.view import View

from chartingperformance.models import EnergyHourly
from chartingperformance.models import EnergyDaily
from chartingperformance.models import EnergyMonthly
from chartingperformance.models import EstimatedMonthly

from flask import jsonify

from sqlalchemy import func
from sqlalchemy.sql import label, and_

class Generation(View):
    """ Genration view query and response methods. """

    def __init__(self, args, house_id):

        super(Generation, self).__init__(args)

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
                filter(table.solar == sub_query).first()

            self.max_solar.append({'date': str(max_solar_query.date),
                                   'solar': str(max_solar_query.max_solar)})

    def get_totals(self, house_id):
        """ Get and store totals from database. """

        if ('year' in self.args['interval']) or ('month' in self.args['interval']):
            self.get_totals_year_month(house_id)

        elif ('day' in self.args['interval']) or ('hour' in self.args['interval']):
            self.get_totals_day_hour(house_id)

    def get_totals_year_month(self, house_id):
        """ Get and store yearly or monthly totals. """

        self.base_query = db_session.query(label('date', func.min(EnergyMonthly.date)),
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

        self.json_totals = {'actual': str(totals.sum_actual),
                            'estimated': str(totals.sum_estimated)}

    def get_totals_day_hour(self, house_id):
        """ Get and store daily or hourly totals. """

        self.base_query = db_session.query(label('date', func.min(EnergyHourly.date)),
                                           label('sum_actual',
                                                 func.sum(EnergyHourly.solar)/1000)).\
            filter(EnergyHourly.house_id == house_id)

        self.filter_query_by_date_range(EnergyHourly)

        totals = self.base_query.one()

        self.json_totals = {'actual': str(totals.sum_actual)}

    def get_items(self):
        """ Get and store rows from database. """

        self.json_items = []

        if ('year' in self.args['interval']) or ('month' in self.args['interval']):
            items = self.group_query_by_interval(EnergyMonthly)
            for item in items:
                data = {'date': str(item.date),
                        'actual': str(item.sum_actual),
                        'estimated': str(item.sum_estimated)}
                self.json_items.append(data)

        elif ('day' in self.args['interval']) or ('hour' in self.args['interval']):
            items = self.group_query_by_interval(EnergyHourly)
            for item in items:
                data = {'date': self.format_date(item.date),
                        'actual': str(item.sum_actual)}
                self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        return jsonify(view='generation',
                       interval=self.args['interval'],
                       max_solar_hour=self.max_solar[0],
                       max_solar_day=self.max_solar[1],
                       totals=self.json_totals,
                       items=self.json_items)
