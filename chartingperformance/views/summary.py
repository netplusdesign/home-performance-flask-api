""" ViewSummary class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.views.view import View

from chartingperformance.models import EnergyHourly
from chartingperformance.models import EnergyMonthly
from chartingperformance.models import HDDHourly
from chartingperformance.models import HDDMonthly

from flask import jsonify

from sqlalchemy import func
from sqlalchemy.sql import label, and_

class Summary(View):
    """ Summary view query and response methods. """

    def __init__(self, args, house_id):

        super(Summary, self).__init__(args)

        if self.success:
            # default to monthly, has more data for 2012
            energy_table = EnergyMonthly
            hdd_table = HDDMonthly
            div = 1

            if 'day' in self.args['interval'] or 'hour' in self.args['interval']:
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

        self.json_totals = {'net': str(totals.sum_adjusted_load),
                            'solar': str(totals.sum_solar),
                            'used': str(totals.sum_used),
                            'hdd': str(totals.sum_hdd)
                           }

    def get_items(self, energy_table):
        """ Get and store rows from database. """

        items = self.group_query_by_interval(energy_table)

        self.json_items = []
        for item in items:
            data = {'date': self.format_date(item.date),
                    'net': str(item.sum_adjusted_load),
                    'solar': str(item.sum_solar),
                    'used': str(item.sum_used),
                    'hdd': str(item.sum_hdd)}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        return jsonify(view='summary',
                       interval=self.args['interval'],
                       totals=self.json_totals,
                       items=self.json_items)
