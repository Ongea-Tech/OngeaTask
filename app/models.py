from datetime import date, datetime
from app import db    
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Association table for Task <-> Category (Many-to-Many)
task_categories = db.Table('task_categories',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.Date, nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    due_date = db.Column(db.Date, nullable=True)

    # Link to categories (Many-to-Many)
    categories = db.relationship('Category', secondary=task_categories,
                                 backref=db.backref('tasks', lazy='dynamic'))
    subtasks = db.relationship('Subtask', backref='task', cascade='all, delete-orphan', lazy=True)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    category_color = db.Column(db.String(20), default='grey')
    category_name = db.Column(db.String(50), default='Medium')


    def mark_as_completed(self):
        self.completed = True
        self.completed_date = date.today()
        self.deleted = False
        self.deleted_date = None

    def move_to_trash(self):
        self.deleted = True
        self.deleted_date = date.today()
        self.completed = False
        self.completed_date = None

    def is_overdue(self):
        if self.due_date and not self.completed and not self.deleted:
            return self.due_date < date.today()
        return False

    @classmethod
    def get_active_tasks(cls, user_id):
        return cls.query.filter_by(user_id=user_id, completed=False, deleted=False).all()

    @classmethod
    def get_completed_tasks(cls, user_id):
        return cls.query.filter_by(user_id=user_id, completed=True, deleted=False).all()

    @classmethod
    def get_deleted_tasks(cls, user_id):
        return cls.query.filter_by(user_id=user_id, deleted=True).all()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_overdue': self.is_overdue(),
            'subtasks': [{'id': st.id, 'title': st.title, 'completed': st.completed} for st in self.subtasks],
            'categories': [{'id': c.id, 'name': c.name, 'color': c.color, 'icon': c.icon} for c in self.categories]
        }


class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)


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
    categories = db.relationship('Category', backref='owner', lazy=True)

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
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), default='#3b82f6')
    icon = db.Column(db.String(50), default='fa-folder')  # Font Awesome class
    description = db.Column(db.Text, nullable=True)
    archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_stats(self):
        """Compute category statistics efficiently."""
        all_tasks = self.tasks.filter_by(deleted=False).all()
        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.completed)
        overdue = sum(1 for t in all_tasks if t.is_overdue())
        completion_rate = round((completed / total * 100)) if total > 0 else 0

        # Last activity: most recent task modified
        last_task = (self.tasks.filter_by(deleted=False)
                     .order_by(Task.id.desc()).first())
        
        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'overdue_tasks': overdue,
            'completion_rate': completion_rate,
            'last_task_id': last_task.id if last_task else None
        }

    def to_dict(self, include_stats=False):
        data = {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'icon': self.icon,
            'description': self.description,
            'archived': self.archived,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }
        if include_stats:
            data.update(self.get_stats())
        return data

    def __repr__(self):
        return f"<Category {self.name}>"