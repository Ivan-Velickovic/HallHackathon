from flask import request, jsonify
from flask_restx import Namespace, Resource, abort, reqparse
from marshmallow import Schema, fields, ValidationError, validates, validate
from util import events, users

api = Namespace('stats', description='Statistics Services')

# Returns a list of events attended by a person in one society
@api.route('/userSocAttendance')
class UserSocAttendance(Resource):
    
    def get(self):
        zID = request.args.get('zID')
        socID = request.args.get('societyID')
        if (zID is None):
            return jsonify({"status": "Failed", "msg": "No zID provided"})
        elif (socID is None):
            return jsonify({"status": "Failed", "msg": "No socID provided"})

        eventsAttended = users.getPersonEventsForSoc(zID, socID)
        if (eventsAttended == "No such user"):
            return jsonify({"status": "Failed", "msg": "No such user"})

        payload = {}
        payload['userName'] = eventsAttended[1]
        payload['societyName'] = eventsAttended[2]
        payload['events'] = []
        for event in eventsAttended[0]:
            eventJSON = {}
            eventJSON['eventID'] = event[0]
            eventJSON['name'] = event[1]
            eventJSON['society'] = event[3]
            eventJSON['eventDate'] = str(event[2])
            eventJSON['points'] = event[4]
            payload['events'].append(eventJSON)
        return jsonify(payload)
        
# For getting information on a set of recurrent events
# Usage:
# GET /api/stat/recurEvent?eventID=?
# Returns:
# {["eventID": "ASDA", "name": "AA meeting", "date": "2020-04-03", "attendance": 41], [...]}
@api.route('/recurEvent', methods=['GET'])
class RecurEventStats(Resource):
    def get(self):
        eventID = request.args.get('eventID')
        if (eventID == None):
            return jsonify({"status": "Failed", "msg": "No eventID"})

        print(events.fetchRecur(eventID))
        return jsonify(events.fetchRecur(eventID))