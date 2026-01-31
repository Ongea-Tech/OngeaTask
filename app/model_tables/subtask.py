# app/model_tables/subtask.py
from ..extensions import db

class Subtask(db.Model):
    __tablename__ = "subtasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)

    def toggle(self):
        self.completed = not self.completed
        return self.completed

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "task_id": self.task_id
        }

    def __repr__(self):
        return f"<Subtask id={self.id} title={self.title} completed={self.completed}>"
