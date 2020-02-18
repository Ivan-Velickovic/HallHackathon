from flask import request, jsonify
from flask_restx import Namespace, Resource, abort, reqparse
from util.users import *
from util.sanitisation_services import sanitize
from marshmallow import Schema, fields, ValidationError, validates, validate
from util import auth_services, users, participation
from schemata.auth_schemata import TokenSchema
from schemata.user_schemata import UserCreationSchema, ZIDSchema

api = Namespace('user', description='User Services')

@api.route('/')
class User(Resource):
    # Returns a list of events this person has attended
    # Usage:
    # GET /api/user
    # Takes:
    # {zID: "z1111111"}
    # Returns:
    # [{"eventID": "1239", "name": "Test Event 0", "society": "UNSW Hall", "eventDate": "2019-11-19"}, {"eventID": "1240", "name": "Coffee Night", "society": "UNSW Hall", "eventDate": "2019-11-20"}]
    @api.response(400, 'Malformed Request')
    # @api.description('Retrieves data on user')
    def get(self):
        if not request.json:
            abort(400, 'Malformed Request')
        # TODO token here
        # Validate data
        try:
            data = ZIDSchema().load(request.get_json())
        except ValidationError as err:
            abort(400, err.messages)
            
        zID = data['zID']
        attendance = users.getUserAttendance(sanitize(zID.lower()))
        return jsonify(attendance)
            
    # For creating a user
    # Usage: 
    # POST /api/user
    # Takes: 
    # {zID: "z1234567", name: "Harrison Steyn", token: "fdsmksfksefoi3m.sadsad3r.fda"}
    # Returns: 
    # {"status": "success"}
    @api.response(400, 'Malformed Request')
    @api.response(401, 'Expired Token')
    @api.response(403, 'Invalid Credentials')
    # @api.description('Creates a user with given details')
    def post(self):
        if not request.json:
            abort(400, 'Malformed Request')
        
        # Validate data
        try:
            data = UserCreationSchema().load(request.get_json())
        except ValidationError as err:
            abort(400, err.messages)
            
        authorized = auth_service.authorize(data['token'], ADMIN)
        
        if (authorized['valid']):
            returnVal = users.createUser(sanitize(data['zID'].lower()), sanitize(data['name']))
            payload = {}
            payload['status'] = returnVal
            return jsonify(payload)
        else:
            return jsonify(authorized)
        abort(400, 'Malformed Request')
        
@api.route('/points')
class Points(Resource):
    
    # Delete user attendance
    # Usage: 
    # DELETE /api/points
    # Takes:
    # {zID: "z5214808", eventID: "13287"}
    # Returns: 
    # {"status": "success"}
    def delete(self):
        data = request.get_json()
        payload = {}
        payload['status'] = participation.deleteUserAttendance(sanitize(data['zID'].lower()), sanitize(data['eventID']))
        return jsonify(payload)
        
    # Update user attendance
    # Usage: 
    # POST /api/points
    # Takes: 
    # {zID: "z5214808", eventID: "13287", points: "10"}
    # Returns: 
    # {"status": "success"}  "points": 1000
    def post(self):
        data = request.get_json()
        payload = {}
        payload['status'] = participation.changePoints(sanitize(data['zID'].lower()), sanitize(data['eventID']), sanitize(str(data['points'])))
        return jsonify(payload)