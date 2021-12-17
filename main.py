from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from rich import print

# Create a flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'This is a super dupper secret key'

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
