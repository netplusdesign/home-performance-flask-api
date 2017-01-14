""" ViewChart class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.views.view import View

from flask import jsonify

from sqlalchemy.sql import text

class Chart(View):
    """ Hourly chart view query and response methods. """

    def __init__(self, args, house_id):

        super(Chart, self).__init__(args)

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
