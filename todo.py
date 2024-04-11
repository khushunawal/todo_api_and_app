from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

# Define Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('todos', lazy=True))

# Route to render the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoints
@app.route('/users', methods=['POST'])
def create_user():
    username = request.json.get('username')
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.json
    new_todo = Todo(title=data['title'], completed=data['completed'], user_id=data['user_id'])
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'message': 'Todo created successfully'}), 201

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify({'id': todo.id, 'title': todo.title, 'completed': todo.completed, 'user_id': todo.user_id})

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    data = request.json
    todo.title = data.get('title', todo.title)
    todo.completed = data.get('completed', todo.completed)
    db.session.commit()
    return jsonify({'message': 'Todo updated successfully'})

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted successfully'})

@app.route('/todos', methods=['GET'])
def get_todos():
    user_id = request.args.get('user_id')
    if user_id:
        todos = Todo.query.filter_by(user_id=user_id).all()
    else:
        todos = Todo.query.all()
    result = []
    for todo in todos:
        result.append({'id': todo.id, 'title': todo.title, 'completed': todo.completed, 'user_id': todo.user_id})
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
