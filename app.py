from datetime import datetime

from flask import Flask, render_template
from flask import request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# with app.app_context():
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # relative path
db: SQLAlchemy = SQLAlchemy(app)  # db is initialized


# making a model
class Todo(db.Model):
    # setting the columns
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # func returns string when element is made
    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index(tasks=[]):
    if request.method == "POST":
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            with app.app_context():
                db.session.add(new_task)
                db.session.commit()
            return redirect('/')

        except Exception as e:
            '''
            tasks = Todo.query.order_by(Todo.date_created).all()
            return 'Issue performing the task'
            '''
            with app.app_context():
                db.session.rollback()  # roll back the transaction if an error occurs
            print(e)
            return 'Issue performing the task'
    else:
        with app.app_context():
            tasks = Todo.query.order_by(Todo.date_created).all()  # get all tasks from the database
        return render_template("index.html", tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    with app.app_context():
        task_to_delete = Todo.qiery.get_or_404(id)

    try:
        with app.app_context():
            db.session.delete(task_to_delete)
            db.session.commit()
        return redirect('/')
    except Exception as e:
        with app.app_context():
            db.session.rollback()  # roll back the transaction if an error occurs
        print(e)
        return 'there was a problem with that route'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    with app.app_context():
        task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            with app.app_context():
                db.session.commit()
            return redirect('/')
        except Exception as e:
            with app.app_context():
                db.session.rollback()  # roll back the transaction if an error occurs
            print(e)
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)


if __name__ == "__main__":
    app.run(debug=True)
