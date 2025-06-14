from app import db 

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.Date, nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.Date, nullable=True)
    subtasks = db.relationship('Subtask', backref='task', cascade='all, delete-orphan', lazy=True)

class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
