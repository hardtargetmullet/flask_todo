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
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo - id: {self.id}, description: {self.description} >'

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())

@app.route('/todos/create', methods=['POST'])
def create():
    error = False
    body = {}
    try:
        text_str = request.get_json()['description']
        task = Todo(description2=text_str)
        db.session.add(task)
        db.session.commit()
        body['description'] = task.description
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