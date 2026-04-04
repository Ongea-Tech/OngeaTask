from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(message="Email is required!"), Email(message="Invalid email")], filters=[lambda x: x.strip() if x else x])
    submit = SubmitField("Submit")

class SignUpForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="User name is required")], filters=[lambda x: x.strip() if x else x])
    first_name = StringField("First Name", validators=[DataRequired(message="First name is required")], filters=[lambda x: x.strip() if x else x])
    last_name = StringField("Last name", validators=[DataRequired(message="Last name is required")], filters=[lambda x: x.strip() if x else x])
    email = StringField("Email", validators=[DataRequired(message="Email is required!"), Email(message="Invalid email")], filters=[lambda x: x.strip() if x else x])
    password = PasswordField('New Password', validators=[DataRequired(message="Password Required"), Length(min=6, max=20, message="Password must be between 6 and 20 characters")])
    confirm_password = PasswordField("Repeat Password", validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LogInForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="User name is required")], filters=[lambda x: x.strip() if x else x])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class ResetPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(message="Email is required!"), Email(message="Invalid email")], filters=[lambda x: x.strip() if x else x])
    submit = SubmitField('Request Password Reset')
