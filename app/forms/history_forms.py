from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired

class HistoryActionForm(FlaskForm):
    action = HiddenField(validators=[DataRequired()])
    task_ids = HiddenField(validators=[DataRequired()])

    reopen = SubmitField("Reopen Task")
    trash = SubmitField("Trash")
