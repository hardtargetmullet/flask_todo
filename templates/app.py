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

    def __repr__(self):
        return f'<Todo - id: {self.id}, description: {self.description} >'

@app.route('/todos/create', methods=['POST'])
def create():
    error = False
    body = {}
    try:
        text_str = request.get_json()['description']
        todo = Todo(description=text_str, completed=False)
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

@app.route('/')
def index():
    return render_template('index.html', todos=Todo.query.order_by('id').all())