#!usr/bin/env python3

from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

MAX_DEPT_ID_LENGTH = 8
MAX_DEPT_NAME_LENGTH = 100

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class DepartmentModel(db.Model):
    id = db.Column(db.String(MAX_DEPT_ID_LENGTH), primary_key=True)
    name = db.Column(db.String(MAX_DEPT_NAME_LENGTH), nullable=False)
    num_of_courses = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Department name = {self.name}'

    def to_json(self):
        return {
            'id': int(self.id),
            'name': self.name,
            'num_of_courses': int(self.num_of_courses)
        }

department_parser = reqparse.RequestParser()
department_parser.add_argument('name', type=str, required=True, help='Department name cannot be blank.')
department_parser.add_argument('num_of_courses', type=int, required=True, help='Number of courses cannot be blank.')

course_parser = reqparse.RequestParser()
course_parser.add_argument('name', type=str, required=True, help='Course name cannot be blank.')
course_parser.add_argument('department', type=str, required=True, help='Course\'s department name cannot be blank.')
course_parser.add_argument('description', type=str, required=True, help='Course description cannot be blank.')
course_parser.add_argument('num_of_hours', type=int, required=True, help='Course number of hours cannot be blank.')
course_parser.add_argument('prerequisites', type=int, required=True, help='Course prerequisites cannot be blank.')
course_parser.add_argument('tccn_id', type=int, required=False)

department_resource_fields = {
    'id': fields.String,
    'name': fields.String,
    'num_of_courses': fields.Integer
}

course_resource_fields = {
    'id': fields.Integer,
    'department': fields.String,
    'name': fields.String,
    'description': fields.String,
    'num_of_hours': fields.Integer,
    'prerequisites': fields.String,
    'tccn_id': fields.Integer
}

class Course(Resource):
    pass

class CourseList(Resource):
    pass

class Department(Resource):
    # Read
    @marshal_with(department_resource_fields)
    def get(self, department_id): #read
        result = DepartmentModel.query.filter_by(id=department_id).first()
        if not result:
            abort(409, message="Department ID doesn't exist.")
        return result

    # Create
    @marshal_with(department_resource_fields)
    def post(self, department_id): #create
        args = department_parser.parse_args()
        result = DepartmentModel.query.filter_by(id=department_id).first()
        if result:
            abort(409, message="Department ID taken.")
        department = DepartmentModel(id=department_id, name=args['name'], num_of_courses=args['num_of_courses'])
        db.session.add(department)
        db.session.commit()
        return department, 201

    # Update
    @marshal_with(department_resource_fields)
    def put(self, department_id):
        '''return department, 204'''
        pass

    # Delete
    def delete(self, department_id):
        result = DepartmentModel.query.filter_by(id=department_id).first()
        if not result:
            abort(409, message="Department ID doesn't exist.")
        db.session.delete(result)
        db.session.commit()
        return '', 204

class DepartmentList(Resource):
    def get(self):
        result = DepartmentModel.query.all()
        return [r.to_json() for r in result]

api.add_resource(DepartmentList, '/')
api.add_resource(Department, '/<string:department_id>')

if __name__ == '__main__':
    app.run(debug=True)