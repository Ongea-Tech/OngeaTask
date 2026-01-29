from app.models import Subtask
from app.extensions import db

class SubtaskService:

    @staticmethod
    def create(task_id: int, title: str) -> Subtask:
        if not title or not title.strip():
            raise ValueError("Subtask title is required!")

        subtask = Subtask(title=title, task_id=task_id)
        db.session.add(subtask)
        db.session.commit()
        return subtask

    @staticmethod
    def get_by_task(task_id: int):
        return Subtask.query.filter_by(task_id=task_id).all()

    @staticmethod
    def toggle(subtask_id: int) -> Subtask:
        subtask = Subtask.query.get(subtask_id)
        if not subtask:
            raise ValueError("Subtask not found")
        subtask.toggle()
        db.session.commit()
        return subtask

    @staticmethod
    def delete(subtask_id: int) -> bool:
        subtask = Subtask.query.get(subtask_id)
        if not subtask:
            raise ValueError("Subtask not found")
        db.session.delete(subtask)
        db.session.commit()
        return True
