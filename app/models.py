from datetime import date
from app import db 
from werkzeug.security import generate_password_hash, check_password_hash

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.Date, nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.Date, nullable=True)
    subtasks = db.relationship('Subtask', backref='task', cascade='all, delete-orphan', lazy=True)

    def mark_as_completed(self):
        """Mark task as completed and update database"""
        self.completed = True
        self.completed_date = date.today()
        self.deleted = False
        self.deleted_date = None
        db.session.commit()
        db.session.refresh(self)

    def move_to_trash(self):
        """Move task to trash and update database"""
        self.deleted = True
        self.deleted_date = date.today()
        self.completed = False
        self.completed_date = None
        db.session.commit()
        db.session.refresh(self)

    @classmethod
    def get_active_tasks(cls):
        """active tasks not completed and not deleted"""
        return cls.query.filter_by(completed=False, deleted=False).all()

    @classmethod
    def get_completed_tasks(cls):
        """completed tasks for a specific date"""
        return cls.query.filter_by(completed=True, deleted=False).all()

    @classmethod
    def get_deleted_tasks(cls):
        """deleted tasks"""
        return cls.query.filter_by(deleted=True).all()
    
class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)