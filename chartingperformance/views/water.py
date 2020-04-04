""" ViewWater class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.views.view import View

from flask import jsonify

from sqlalchemy.sql import text

class Water(View):
    """ Water view query and response methods. """

    def __init__(self, args, house_id):

        super(Water, self).__init__(args)

        if ('day' in self.args['interval']) or ('hour' in self.args['interval']):
            self.success = False
            self.error = {'error':'Interval not available.'}
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

        grp = ""

        if 'month' in self.args['interval']:
            grp = ", MONTH(e.date) "

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

        return jsonify(view='water',
                       interval=self.args['interval'],
                       totals=self.json_totals,
                       items=self.json_items)