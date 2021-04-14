#!usr/bin/env python3

from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class CourseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Course name = {self.name}'

    def to_json(self):
        return {
            'id': int(self.id),
            'name': self.name
        }

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Name cannot be blank.')

resource_fields = {
    'id': fields.Integer,
    'name': fields.String
}

class Course(Resource):
    # Read
    @marshal_with(resource_fields)
    def get(self, course_id): #read
        result = CourseModel.query.filter_by(id=course_id).first()
        if not result:
            abort(409, message="Course id doesn't exist.")
        return result

    # Create
    @marshal_with(resource_fields)
    def post(self, course_id): #create
        args = parser.parse_args()
        result = CourseModel.query.filter_by(id=course_id).first()
        if result:
            abort(409, message="Course id taken.")
        course = CourseModel(id=course_id, name=args['name'])
        db.session.add(course)
        db.session.commit()
        return course, 201

    # Update
    @marshal_with(resource_fields)
    def put(self, course_id):
        '''return course, 204'''
        pass

    # Delete
    def delete(self, course_id):
        result = CourseModel.query.filter_by(id=course_id).first()
        if not result:
            abort(409, message="Course id doesn't exist.")
        db.session.delete(result)
        db.session.commit()
        return '', 204

class CourseList(Resource):
    def get(self):
        result = CourseModel.query.all()
        return [r.to_json() for r in result]

api.add_resource(CourseList, '/', '/course')
api.add_resource(Course, '/course/<int:course_id>')

if __name__ == '__main__':
    app.run(debug=True)