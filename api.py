#!usr/bin/env python3

from flask import Flask
from flask_restful import Api, Resource, abort, fields, marshal_with, reqparse
from flask_sqlalchemy import SQLAlchemy

MAX_DEPT_ID_LENGTH = 10
MAX_DEPT_NAME_LENGTH = 100
MAX_COURSE_ID_LENGTH = 20
MAX_COURSE_NAME_LENGTH = 200
MAX_COURSE_DESC_LENGTH = 1000
MAX_COURSE_PREREQ_LENGTH = 200

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

department_resource_fields = {
    'id': fields.String,
    'name': fields.String,
    'num_of_courses': fields.Integer
}

course_resource_fields = {
    'id': fields.String,
    'course_num': fields.Integer,
    #'department_id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'num_of_hours': fields.Integer,
    'prerequisites': fields.String,
    'tccn_id': fields.String,
    'department_model_id': fields.String
}

class DepartmentModel(db.Model):
    id = db.Column(db.String(MAX_DEPT_ID_LENGTH), primary_key=True)
    name = db.Column(db.String(MAX_DEPT_NAME_LENGTH), nullable=False)
    num_of_courses = db.Column(db.Integer, nullable=False)
    courses = db.relationship('CourseModel', backref='department_model') # One-to-many relationship

    def __repr__(self):
        return f'Department name = {self.name}, number of courses = {self.num_of_courses}'

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'num_of_courses': int(self.num_of_courses)
        }

class CourseModel(db.Model):
    id = db.Column(db.String(MAX_COURSE_ID_LENGTH), primary_key=True)
    course_num = db.Column(db.Integer, nullable=False)
    #department_id = db.Column(db.String(MAX_DEPT_ID_LENGTH), nullable=False)
    name = db.Column(db.String(MAX_COURSE_NAME_LENGTH), nullable=False)
    description = db.Column(db.String(MAX_COURSE_DESC_LENGTH), nullable=False)
    num_of_hours = db.Column(db.Integer, nullable=False)
    prerequisites = db.Column(db.String(MAX_COURSE_PREREQ_LENGTH), nullable=False)
    tccn_id = db.Column(db.String(MAX_COURSE_ID_LENGTH), nullable=False)
    department_model_id = db.Column(db.String(MAX_DEPT_ID_LENGTH), db.ForeignKey('department_model.id'), nullable=False)
    # Table name of DepartmentModel -> department_model
    
    def __repr__(self):
        return f'Course name = {self.name}'

    def to_json(self):
        return {
            'id': self.id,
            'course_num': int(self.course_num),
            #'department_id': self.department_id,
            'name': self.name,
            'description': self.description,
            'num_of_hours': int(self.num_of_hours),
            'prerequisites': self.prerequisites,
            'tccn_id': self.tccn_id,
            'department_model_id': self.department_model_id
        }

# Only do first time/when a column is added, will rewrite database if done again
# Try if 'OperationalError: no such column' happens
#db.create_all()

# Argument Parsers - Validates POST/PUT requests and ensures necessary info is sent with the request
department_put_args = reqparse.RequestParser()
course_put_args = reqparse.RequestParser()

# Necessary arguments for department and course POST requests
department_put_args.add_argument('id', type=str, required=True, help='Department initials cannot be blank.')
department_put_args.add_argument('name', type=str, required=True, help='Department name cannot be blank.')
department_put_args.add_argument('num_of_courses', type=int, required=True, help='Number of courses cannot be blank.')

course_put_args.add_argument('id', type=str, required=True, help='Course ID cannot be blank.')
course_put_args.add_argument('course_num', type=int, required=True, help='Course number cannot be blank.')
#course_put_args.add_argument('department_id', type=str, required=True, help='Course\'s department ID cannot be blank.')
course_put_args.add_argument('name', type=str, required=True, help='Course name cannot be blank.')
course_put_args.add_argument('description', type=str, required=True)
course_put_args.add_argument('num_of_hours', type=int, required=True, help='Course number of hours cannot be blank.')
course_put_args.add_argument('prerequisites', type=str, required=True)
course_put_args.add_argument('tccn_id', type=str, required=True)
course_put_args.add_argument('department_model_id', type=str, required=True)

class HomePage(Resource):
    def get(self):
        result_departments = DepartmentModel.query.all()
        result_courses = CourseModel.query.all()
        return [r.to_json() for r in result_departments] + [r.to_json() for r in result_courses]

class DepartmentList(Resource):
    def get(self):
        result = DepartmentModel.query.all()
        return [r.to_json() for r in result]

class CourseList(Resource):
    def get(self):
        result = CourseModel.query.all()
        return [r.to_json() for r in result]

class Department(Resource):
    @marshal_with(department_resource_fields) # Decorator that serializes result with given fields into JSON format
    def get(self, department_id):
        result = DepartmentModel.query.filter_by(id=department_id).first() # Returns DepartmentModel instance
        if not result:
            abort(409, message="Department ID doesn't exist.")
        return result, 200

    @marshal_with(department_resource_fields)
    def put(self, department_id):
        args = department_put_args.parse_args()
        result = DepartmentModel.query.filter_by(id=department_id).first()
        if result:
            abort(409, message="Department ID taken.")
        department = DepartmentModel(id=department_id, name=args['name'], num_of_courses=args['num_of_courses'])
        db.session.add(department)
        db.session.commit()
        return department, 201
        
    def delete(self, department_id):
        result = DepartmentModel.query.filter_by(id=department_id).first()
        if not result:
            abort(409, message="Department ID doesn't exist.")
        db.session.delete(result)
        db.session.commit()
        return '', 204

class Course(Resource):
    @marshal_with(course_resource_fields)
    def get(self, course_id):
        result = CourseModel.query.filter_by(id=course_id).first() # Returns CourseModel instance
        if not result:
            abort(409, message="Course ID doesn't exist.")
        return result, 200
    
    @marshal_with(course_resource_fields)
    def put(self, course_id):
        args = course_put_args.parse_args()
        result = CourseModel.query.filter_by(id=course_id).first()
        if result:
            abort(409, message="Course ID taken.")
        course = CourseModel(id=course_id, course_num=args['course_num'], #department_id=args['department_id'], 
            name=args['name'], description=args['description'], num_of_hours=args['num_of_hours'], 
            prerequisites=args['prerequisites'], tccn_id=args['tccn_id'], department_model_id=args['department_model_id'])
        db.session.add(course)
        db.session.commit()
        return course, 201

    def delete(self, course_id):
        result = CourseModel.query.filter_by(id=course_id).first()
        if not result:
            abort(409, message="Course ID doesn't exist.")
        db.session.delete(result)
        db.session.commit()
        return '', 204

api.add_resource(HomePage, '/')
api.add_resource(DepartmentList, '/department')
api.add_resource(Department, '/department/<string:department_id>')
api.add_resource(CourseList, '/course')
api.add_resource(Course, '/course/<string:course_id>')

if __name__ == '__main__':
    app.run(debug=True)