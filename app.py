import sys
from flask import Flask
from flask import abort
from flask import jsonify
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:password@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo - id: {self.id}, description: {self.description}, completed: {self.completed} >'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TodoList - id: {self.id}, name - {self.name}>'

@app.route('/todos/create', methods=['POST'])
def create():
    error = False
    body = {}
    try:
        print("almost there")
        text_str = request.get_json()['description']
        todo = Todo(description=text_str, completed=False, list_id=1)
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['completed'] = todo.completed
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()  
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        return abort(400)
    else:
        return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    error = False
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        return abort(500)
    else:
        return redirect(url_for('index'))

@app.route('/list/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
    error = False
    try:
        completed = request.get_json()['completed']
        todo_list = TodoList.query.get(list_id)
        for todo in todo_list.todos:
            todo.completed = not todo.completed
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        return abort(500)
    else:
        return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    error = False
    try:
        print("Trying to Erase: ", todo_id)
        todo = Todo.query.order_by('id').get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        print("SOMETHING FUCKED UP")
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        return abort(500)
    else:
        return jsonify({ 'success': True })

@app.route('/list/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html',
    lists=TodoList.query.all(),
    active_list=TodoList.query.get(list_id),
    todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/list/create', methods=['POST'])
def create_list():
    error = False
    body = {}
    try:
        text_str = request.get_json()['name']
        todo_list = TodoList(name=text_str)
        db.session.add(todo_list)
        db.session.commit()
        print(todo_list)
        body['id'] = todo_list.id
        #body['completed'] = todo.completed
        body['name'] = todo_list.name
    except:
        error = True
        db.session.rollback()  
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        return abort(500)
    else:
        return jsonify(body)

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))