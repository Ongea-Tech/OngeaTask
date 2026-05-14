from datetime import date, datetime, timezone
from app import db    
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    due_date = db.Column(db.DateTime, nullable=True)
    estimated_minutes = db.Column(db.Integer, nullable=True)
    last_nudged_at = db.Column(db.DateTime, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', backref='tasks')
    subtasks = db.relationship('Subtask', backref='task', cascade='all, delete-orphan', lazy=True)

    def mark_as_completed(self):
        """Mark task as completed and update database"""
        self.completed = True
        self.completed_date = date.today()
        self.deleted = False
        self.deleted_date = None
        db.session.refresh(self)

    def move_to_trash(self):
        """Move task to trash and update database"""
        self.deleted = True
        self.deleted_date = date.today()
        self.completed = False
        self.completed_date = None
        db.session.refresh(self)

    @classmethod
    def get_active_tasks(cls, user_id):
        """active tasks not completed and not deleted"""
        return cls.query.filter_by(user_id = user_id, completed=False, deleted=False).all()

    @classmethod
    def get_completed_tasks(cls, user_id):
        """completed tasks for a specific date"""
        return cls.query.filter_by(user_id = user_id, completed=True, deleted=False).all()

    @classmethod
    def get_deleted_tasks(cls, user_id):
        """deleted tasks"""
        return cls.query.filter_by(user_id = user_id, deleted=True).all()
    
class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

class Notification(db.Model):
    __tablename__ ="notification"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    nudge_type = db.Column(db.String(50), nullable=False, default="general")
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    read = db.Column(db.Boolean, default=False)
    task = db.relationship('Task', backref='notifications')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    image_filename = db.Column(db.String(200), default='images/profile.png')
    motivation_message = db.Column(db.Text, nullable=True)
    motivation_date = db.Column(db.Date, nullable=True)

    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "image_filename": self.image_filename,
            "motivation_message": self.motivation_message,
            "motivation_date": self.motivation_date.isoformat() if self.motivation_date else None
        }
    def __repr__(self):
        return f"<User {self.username}>"
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(20), default='#cccccc')  # New field for urgency color

    def __repr__(self):
        return f"<Category {self.name}>"

class CategoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    selected = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f"<CategoryItem {self.title} (Category {self.category_id})>"