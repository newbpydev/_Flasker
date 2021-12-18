from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

from flask_script import Manager
from flask_migrate import Migrate
from datetime import datetime

from rich import print

# Create a flask instance
app = Flask(__name__)
# Secret Key
app.config['SECRET_KEY'] = 'This is a super dupper secret key'

# Add database settings
### Old SQLite database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

### MYSQL database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/dbname'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
# ***** Migration for the db for when I need to update the columns
migrate = Migrate(app, db)
manager = Manager(app)

now = datetime.utcnow()


# create a DB model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=now)

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name


db.create_all()


# create a user form class
class UserForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()], render_kw={'autofocus': True})
    email = StringField(label="Email?", validators=[DataRequired()])
    favorite_color = StringField(label="Favorite Color")
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
                favorite_color=form.favorite_color.data,
            )
            db.session.add(new_user)
            db.session.commit()

            form.name.data = ''
            form.email.data = ''
            form.favorite_color.data = ''
            flash('User added successfully!')

    our_users = Users.query.order_by(Users.date_added).all()

    return render_template('add_user.html', form=form, name=person_name, our_users=our_users)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    form = UserForm()
    # Get the user from db or return 404 if not found in database
    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form.get('name')
        name_to_update.email = request.form.get('email')
        name_to_update.favorite_color = request.form.get('favorite_color')
        try:
            db.session.commit()
            flash('User updated successfully!')
            return render_template('update_user.html', form=form, name_to_update=name_to_update)
        except:
            flash('Looks like there was a problem, try again!')
            return render_template('update_user.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('update_user.html', form=form, name_to_update=name_to_update)


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
