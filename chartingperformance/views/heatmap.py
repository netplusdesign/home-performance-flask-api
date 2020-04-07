""" ViewHeatmap class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.views.view import View

from flask import jsonify

from sqlalchemy.sql import text

class Heatmap(View):
    """ Daily heatmap view query and response methods. """

    def __init__(self, args, house_id):

        super(Heatmap, self).__init__(args)

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
                    'net': str(item.net),
                    'solar': str(item.solar),
                    'used': str(item.used),
                    'outdoor_deg_min': str(item.outdoor_deg_min),
                    'outdoor_deg_max': str(item.outdoor_deg_max),
                    'hdd': str(item.hdd),
                    'water_heater': str(item.water_heater),
                    'ashp': str(item.ashp),
                    'water_pump': str(item.water_pump),
                    'dryer': str(item.dryer),
                    'washer': str(item.washer),
                    'dishwasher': str(item.dishwasher),
                    'stove': str(item.stove),
                    'refrigerator': str(item.refrigerator),
                    'living_room': str(item.living_room),
                    'aux_heat_bedrooms': str(item.aux_heat_bedrooms),
                    'aux_heat_living': str(item.aux_heat_living),
                    'study': str(item.study),
                    'barn': str(item.barn),
                    'basement_west': str(item.basement_west),
                    'basement_east': str(item.basement_east),
                    'ventilation': str(item.ventilation),
                    'ventilation_preheat': str(item.ventilation_preheat),
                    'kitchen_recept_rt': str(item.kitchen_recept_rt),
                    'all_other': str(item.all_other)}
            self.json_items.append(data)

    def get_response(self):
        """ Return response in json format. """

        if not self.success:
            return jsonify(self.error)

        return jsonify(view='heatmap',
                       interval=self.args['interval'],
                       days=self.json_items)
