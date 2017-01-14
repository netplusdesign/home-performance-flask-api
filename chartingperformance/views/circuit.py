""" CircuitDict class """
# pylint: disable=no-member
from chartingperformance import db_session
from chartingperformance.models import Circuits
from flask import jsonify

class CircuitDict(object):
    """ Helper query and response methods. Used for circuits endpoint and in ViewUsage class. """

    def __init__(self, house_id):

        self.circuits = self.get_circuits(house_id)

    def get_circuits(self, house_id):
        """ Get, store and return list of circuits from database. """

        circuits = db_session.query(Circuits). \
            filter(Circuits.house_id == house_id).all()

        self.json_items = []
        for circuit in circuits:
            data = {'circuit_id': circuit.circuit_id,
                    'name': circuit.name,
                    'description': circuit.description}
            self.json_items.append(data)

        return circuits

    def get_response(self):
        """ Return response in json format. """

        return jsonify(circuits=self.json_items)
