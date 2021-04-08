from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import requests

cast = {
    'id': 0,
    'name': 'John Wick',
    'played_by': 'Keanu Reeves'
}

app = Flask(__name__)
api = Api(app)

def abort_if_cast_doesnt_exist(cast_id):
    if cast_id not in cast:
        abort(404, message=f"ID {cast_id} doesn't exist")

class Cast_Member(Resource):
    def get(self, cast_id):
        abort_if_cast_doesnt_exist(cast_id)
        return cast[cast_id]

class Full_Cast(Resource):
    def get(self):
        return cast

api.add_resource(Full_Cast, '/', '/cast')
api.add_resource(Cast_Member, '/cast/<cast_id>')

if __name__ == '__main__':
    app.run(debug=True)