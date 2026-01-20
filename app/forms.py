from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class TaskForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Task title is required."),
            Length(min=2, max=100, message="Title must be between 2 and 100 characters."),
        ],
        filters=[lambda x: x.strip() if x else x],
    )

    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=2000, message="Description is too long.")],
        filters=[lambda x: x.strip() if x else x],
    )

    submit = SubmitField("Save")

