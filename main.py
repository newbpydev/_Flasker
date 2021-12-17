from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from rich import print

# Create a flask instance
app = Flask(__name__)
# Secret Key
app.config['SECRET_KEY'] = 'This is a super dupper secret key'
# Add database settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Initialize the database
db = SQLAlchemy(app)

now = datetime.utcnow()

# create a DB model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=now)

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name

db.create_all()


# create a user form class
class UserForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()], render_kw={'autofocus': True})
    email = StringField(label="Email?", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


# create a form class
class NameForm(FlaskForm):
    name = StringField(label="What's your name?", validators=[DataRequired()])
    submit = SubmitField(label="Submit")

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/user/add', methods=['POST', 'Get'])
def add_user():
    person_name = None
    form = UserForm()

    if form.validate_on_submit():
        user_info = db.session.query(Users).filter_by(email=form.email.data).first()
        if user_info is None:
            new_user = Users(
                name=form.name.data,
                email=form.email.data,
            )
            db.session.add(new_user)
            db.session.commit()

            form.name.data = ''
            form.email.data = ''
            flash('User added successfully!')

    our_users = Users.query.order_by(Users.date_added).all()

    return render_template('add_user.html', form=form, name=person_name, our_users=our_users)


# create a name page
@app.route('/name', methods=['Get', 'Post'])
def name():
    person_name = None
    form = NameForm()

    print(f'monkey {person_name}')
    if form.validate_on_submit():
        person_name = form.name.data
        form.name = ''

        flash(message='Form submitted successfully')

    return render_template('name.html', name=person_name, form=form)



# Create custom error pages
# invalid URL
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# invalid URL
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
