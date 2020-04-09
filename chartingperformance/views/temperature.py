""" ViewTemperature class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.views.view import View

from chartingperformance.models import TemperatureHourly
from chartingperformance.models import HDDHourly

from flask import jsonify

from sqlalchemy import func
from sqlalchemy.sql import label, and_

class Temperature(View):
    """ Temperature view query and response methods. """

    def __init__(self, args, house_id):

        super(Temperature, self).__init__(args)

        if self.success:
            self.get_totals(house_id)
            self.get_items()

    def get_totals(self, house_id):
        """ Get and store totals from database. """

        self.base_query = db_session.\
                          query(label('date', func.min(TemperatureHourly.date)),
                                label('min_temperature',
                                      func.min(TemperatureHourly.temperature)),
                                label('max_temperature',
                                      func.max(TemperatureHourly.temperature)),
                                label('avg_temperature',
                                      func.avg(TemperatureHourly.temperature)),
                                label('min_humidity',
                                      func.min(TemperatureHourly.humidity)),
                                label('max_humidity',
                                      func.max(TemperatureHourly.humidity)),
                                label('sum_hdd',
                                      func.sum(HDDHourly.hdd))).\
            outerjoin(HDDHourly, and_(HDDHourly.date == TemperatureHourly.date,
                                      HDDHourly.house_id == TemperatureHourly.house_id)).\
            filter(and_(TemperatureHourly.house_id == house_id,
                        TemperatureHourly.device_id == self.args['location']))

        self.filter_query_by_date_range(TemperatureHourly)

        totals = self.base_query.one()

        self.json_totals = {'min_temperature': str(totals.min_temperature),
                            'max_temperature': str(totals.max_temperature),
                            'avg_temperature': str(totals.avg_temperature),
                            'sum_hdd': str(totals.sum_hdd),
                            'min_humidity': str(totals.min_humidity),
                            'max_humidity': str(totals.max_humidity)}

    def get_items(self):
        """ Get and store rows from database. """

        items = self.group_query_by_interval(TemperatureHourly)

        self.json_items = []
        for item in items:
            data = {'date': self.format_date(item.date),
                    'min_temperature': str(item.min_temperature),
                    'max_temperature': str(item.max_temperature),
                    'avg_temperature': str(item.avg_temperature),
                    'sum_hdd': str(item.sum_hdd),
                    'min_humidity': str(item.min_humidity),
                    'max_humidity': str(item.max_humidity)}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        return jsonify(view='temperature',
                       interval=self.args['interval'],
                       location=self.args['location'],
                       totals=self.json_totals,
                       items=self.json_items)
