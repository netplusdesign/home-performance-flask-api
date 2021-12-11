""" ViewBasetemp class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.views.view import View

from flask import jsonify

from sqlalchemy.sql import text, column

class Basetemp(View):
    """ Basetemp analysis view query and response methods. """

    def __init__(self, args, house_id):

        super(Basetemp, self).__init__(args)

        if self.success:
            self.get_items(house_id)

    def get_items(self, house_id):
        """ Get and store points (primarily hdd and ashp values) from database. """

        items = db_session.query(column("hdd"), column("ashp"),
                                 column("temperature"), column("date"), column("solar"))

        if self.args['start'] is not None and self.args['end'] is not None:
            date_range = " AND date BETWEEN :start AND :end "

        elif self.args['start'] is not None:
            date_range = " AND date >= :start "

        elif self.args['end'] is not None:
            date_range = " AND date < :end "

        elif self.args['start'] is None and self.args['end'] is None:
            date_range = ""

        if 'hour' in self.args['interval']:
            sql = """SELECT e.date AS 'date',
                     t.hdd AS 'hdd',
                     e.ashp/1000.0 AS 'ashp',
                     t.temperature AS 'temperature',
                     e.solar/1000.0 AS 'solar'
                  """

        else:
            sql = """SELECT MIN(e.date) AS 'date',
                     SUM(t.hdd) AS 'hdd',
                     SUM(e.ashp)/1000.0 AS 'ashp',
                     AVG(t.temperature) AS 'temperature',
                     SUM(e.solar)/1000.0 AS 'solar'
                  """

        sql = sql + \
        """FROM (SELECT date, solar, ashp
           FROM energy_hourly
           WHERE house_id = :house_id
           AND solar > -500
           AND ashp > 50 %s) e
           LEFT JOIN
           (SELECT date, temperature, (:base - temperature) / 24.0 AS 'hdd'
           FROM temperature_hourly
           WHERE house_id = :house_id
           AND device_id = 0
           AND temperature <= :base %s) t ON e.date = t.date
           WHERE t.date = e.date
        """ % (date_range, date_range)

        if self.args['interval'] == 'year':
            sql = sql + "GROUP BY YEAR(t.date)"

        if self.args['interval'] == 'month':
            sql = sql + "GROUP BY YEAR(t.date), MONTH(t.date)"

        if self.args['interval'] == 'day':
            sql = sql + "GROUP BY CAST(t.date AS DATE)"

        items = items.from_statement(text(sql))
        items = items.params(house_id=house_id,
                             base=self.args['base'],
                             start=self.is_date(self.args['start']),
                             end=self.is_date(self.args['end'])).all()

        self.json_items = []
        for item in items:
            data = {'date': str(self.format_date(item.date)),
                    'solar': str(item.solar),
                    'ashp': str(item.ashp),
                    'temperature': str(item.temperature),
                    'hdd': str(item.hdd)}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """
        if not self.success:
            return jsonify(self.error)

        return jsonify(view='heat',
                       base=self.args['base'],
                       interval=self.args['interval'],
                       points=self.json_items)
