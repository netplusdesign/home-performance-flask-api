""" View parent class """
# pylint: disable=no-member
from sqlalchemy import func
from sqlalchemy.sql import or_

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
            self.error = {'error':'No arguments found.'}
        self.base_query = None
        self.json_totals = None
        self.json_items = None
        self.json_circuit = None

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

    def format_date(self, date):
        """ Return formatted date string based on interval. """

        if 'hour' in self.args['interval']:
            date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            date_str = date.strftime("%Y-%m-%d")

        return date_str

    def set_args(self, args):
        """ Return dict with parameters included in GET. """

        interval = self.validate_interval(args.get('interval'),
                                          self.valid_intervals)

        start = args.get('start', None)
        if start != '' and start is not None:
            try:
                start = moment.date(start)
            except ValueError:
                start = None
        else:
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
