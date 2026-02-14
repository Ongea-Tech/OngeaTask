from flask_wtf import FlaskForm 
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, HiddenField 
from wtforms.validators import DataRequired, Length, Optional


class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(message= "Task title is required."), Length(min=2, max=100, message="Title must be between 2 and 100 characters.")], filters=[lambda x: x.strip() if x else x])
    description = TextAreaField('Description', validators=[Optional(), Length(min=2, max=2000, message="Description cannot exceed 2000 characters.")], filters=[lambda x: x.strip() if x else x])
    submit = SubmitField('Create Task')

class SignupForm(FlaskForm):
    username = StringField('Username*', validators=[DataRequired(message="Username is required."), Length(min=2, max=50, message="Username must be between 2 and 50 characters.")], filters=[lambda x: x.strip() if x else x])
    first_name = StringField('First Name*', validators=[DataRequired(message="First name is required."), Length(min=2, max=50, message="First name must be between 2 and 50 characters.")], filters=[lambda x: x.strip() if x else x])
    last_name = StringField('Last Name*', validators=[DataRequired(message="Last name is required."), Length(min=2, max=50, message="Last name must be between 2 and 50 characters.")], filters=[lambda x: x.strip() if x else x])
    email = StringField('Email*', validators=[DataRequired(message="Email is required."), Length(min=5, max=100, message="Email must be between 5 and 100 characters.")], filters=[lambda x: x.strip() if x else x])
    password = StringField('Password*', validators=[DataRequired(message="Password is required."), Length(min=6, max=100, message="Password must be between 6 and 100 characters.")])
    confirm_password = StringField('Confirm Password*', validators=[DataRequired(message="Please confirm your password."), Length(min=6, max=100, message="Password must be between 6 and 100 characters.")])
    submit = SubmitField('Sign Up*')

class MoveToTrashForm(FlaskForm):
    trash_ids = HiddenField()
    submit = SubmitField("🗑️ Move to Trash")
