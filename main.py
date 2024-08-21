import os

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
bootstrap = Bootstrap(app)

# secret key
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
db = SQLAlchemy(app)


# In-memory list to store to-dos
# ToDoList Configuration with SQL so it accessible in the code
class ToDoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(250), unique=True, nullable=False)
    checked = db.Column(db.Boolean, nullable=False)


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    todos = [column for column in db.session.query(ToDoList).all()]
    return render_template('index.html', todos=todos, edit_mode=False)


@app.route('/add', methods=['GET', 'POST'])
def add_todo():
    if request.method == 'POST':
        todo = ToDoList(
            item=request.form["item"],
            checked=False
        )
        db.session.add(todo)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:todo_id>', methods=['GET', 'POST', 'PUT'])
def edit_todo(todo_id):
    if request.method == 'POST':
        todo = db.session.query(ToDoList).get(todo_id)
        todo.item = request.form["edited_item"]
        db.session.commit()
        return redirect(url_for('index'))
    else:
        todos = [column for column in db.session.query(ToDoList).all()]
        return render_template('index.html', todos=todos, edit_mode=True, id=todo_id)


@app.route('/done/<int:todo_id>')
def done_todo(todo_id):
    todo = db.session.query(ToDoList).get(todo_id)
    todo.checked = not todo.checked  ## toggle checked state
    db.session.commit()
    if todo.checked:
        update_todo = ToDoList(
            item=todo.item,
            checked=todo.checked
        )

        db.session.delete(todo)  ## remove from database
        db.session.commit()

        db.session.add(update_todo)  ## move item to bottom of list
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    todo = db.session.query(ToDoList).get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
