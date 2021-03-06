from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy

from flask_script import Manager
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    # password magic
    password_hash = db.Column(db.String(128), nullable=False)

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name


# Create a Blog Post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    author = db.Column(db.String(250), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    slug = db.Column(db.String(255), nullable=False)


db.create_all()


# create a user form class
class UserForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()], render_kw={'autofocus': True})
    email = StringField(label="Email?", validators=[DataRequired()])
    favorite_color = StringField(label="Favorite Color")
    password_hash = PasswordField(label="Password", validators=[DataRequired(), EqualTo('password_hash2', message="Passwords must match")])
    password_hash2 = PasswordField(label="Confirm Password", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


# create a form class
class NameForm(FlaskForm):
    name = StringField(label="What's your name?", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


# Create a blog form
class PostForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    content = StringField(label="Content", validators=[DataRequired()], widget=TextArea())
    author = StringField(label="Author", validators=[DataRequired()])
    slug = StringField(label="Slug", validators=[DataRequired()])
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
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, method='sha256')

            new_user = Users(
                name=form.name.data,
                email=form.email.data,
                favorite_color=form.favorite_color.data,
                password_hash=hashed_pw,
            )
            db.session.add(new_user)
            db.session.commit()

            form.name.data = ''
            form.email.data = ''
            form.favorite_color.data = ''
            form.password_hash.data = ''

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
        return render_template('update_user.html', form=form, name_to_update=name_to_update, id=id)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    person_name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()

        flash('User Delete Successfully!')
        our_users = Users.query.order_by(Users.date_added).all()
        return render_template('add_user.html', form=form, name=person_name, our_users=our_users)
    except:
        flash('There was a problem deleting user, try again!')
        return render_template('add_user.html', form=form, name=person_name, our_users=our_users)
    # finally:
    #     return render_template('add_user.html', form=form, name=person_name, our_users=our_users)

    return render_template('delete_user.html')


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


@app.route('/add-post', methods=['POST', 'GET'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            author=form.author.data,
            slug=form.slug.data,
        )
        # Add post to database
        db.session.add(post)
        db.session.commit()

        flash('Blog post added successfully')

        # clear the form before resending
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

    return render_template('add_post.html',
                           form=form)


@app.route('/posts')
def posts():

    return render_template('posts.html')


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
