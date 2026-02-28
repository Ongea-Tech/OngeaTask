from app.models import Task
from app import db

class TaskService:
    def create(self, *, title, description=None):
        if not title or not title.strip():
            raise ValueError("Task name is required")
        t = Task(title=title.strip(), description=description, completed=False)
        db.session.add(t)
        db.session.commit()
        return t