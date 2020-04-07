""" ViewHdd class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.views.view import View

from chartingperformance.models import Houses
from chartingperformance.models import EnergyDaily
from chartingperformance.models import TemperatureHourly
from chartingperformance.models import HDDDaily
from chartingperformance.models import HDDMonthly
from chartingperformance.models import EstimatedMonthly

from flask import jsonify

from sqlalchemy import func
from sqlalchemy.sql import label, and_

class Hdd(View):
    """ Hdd view query and response methods. """

    def __init__(self, args, house_id):

        super(Hdd, self).__init__(args)

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
                                  'temperature': str(min_temperature_hour_query.temperature)}

    def get_coldest_day(self, house_id):
        """ Get and store dict of coldest day from database. """

        self.base_query = db_session.query(label('hdd', func.max(HDDDaily.hdd))).\
            filter(HDDDaily.house_id == house_id)

        sub_query = self.filter_query_by_date_range(HDDDaily)

        min_hdd_day_query = db_session.query(HDDDaily.date, HDDDaily.hdd).\
            filter(HDDDaily.hdd == sub_query).one()

        self.json_coldest_day = {'date': str(min_hdd_day_query.date),
                                 'temperature': str(min_hdd_day_query.hdd)}
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

        self.json_totals = {'actual': str(totals.sum_actual),
                            'estimated': str(totals.sum_estimated),
                            'ashp_heating_season': str(self.total_hdd_and_ashp_in_heating_season_query.total_ashp),
                            'hdd_heating_season': str(self.total_hdd_and_ashp_in_heating_season_query.total_hdd)}

    def get_items(self):
        """ Get and store rows from database. """

        items = self.group_query_by_interval(HDDMonthly)

        self.json_items = []
        for item in items:
            data = {'date': str(item.date),
                    'actual': str(item.sum_actual),
                    'estimated': str(item.sum_estimated)}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        return jsonify(view='hdd',
                       interval=self.args['interval'],
                       coldest_hour=self.json_coldest_hour,
                       coldest_day=self.json_coldest_day,
                       iga=str(self.iga_query.iga),
                       totals=self.json_totals,
                       items=self.json_items)
