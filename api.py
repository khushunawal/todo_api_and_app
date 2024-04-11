from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)
api = Api(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('todos', lazy=True))

class UserResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username is required')
        args = parser.parse_args()

        new_user = User(username=args['username'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

class TodoResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, help='Title is required')
        parser.add_argument('completed', type=bool, default=False)
        parser.add_argument('user_id', type=int, required=True, help='User ID is required')
        args = parser.parse_args()

        new_todo = Todo(title=args['title'], completed=args['completed'], user_id=args['user_id'])
        db.session.add(new_todo)
        db.session.commit()
        return {'message': 'Todo created successfully'}, 201

    def get(self, todo_id):
        todo = Todo.query.get(todo_id)
        if not todo:
            return {'error': 'Todo not found'}, 404
        return {'id': todo.id, 'title': todo.title, 'completed': todo.completed, 'user_id': todo.user_id}

    def put(self, todo_id):
        todo = Todo.query.get(todo_id)
        if not todo:
            return {'error': 'Todo not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('completed', type=bool)
        args = parser.parse_args()

        if args['title']:
            todo.title = args['title']
        if args['completed'] is not None:
            todo.completed = args['completed']

        db.session.commit()
        return {'message': 'Todo updated successfully'}

    def delete(self, todo_id):
        todo = Todo.query.get(todo_id)
        if not todo:
            return {'error': 'Todo not found'}, 404
        db.session.delete(todo)
        db.session.commit()
        return {'message': 'Todo deleted successfully'}

class TodoListResource(Resource):
    def get(self):
        user_id = request.args.get('user_id')
        if user_id:
            todos = Todo.query.filter_by(user_id=user_id).all()
        else:
            todos = Todo.query.all()

        result = [{'id': todo.id, 'title': todo.title, 'completed': todo.completed, 'user_id': todo.user_id} for todo in todos]
        return result

api.add_resource(UserResource, '/users')
api.add_resource(TodoResource, '/todos', '/todos/<int:todo_id>')
api.add_resource(TodoListResource, '/todos_list')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
