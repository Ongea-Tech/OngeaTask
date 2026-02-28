from datetime import date, timedelta
from app.models import Task
from app.extensions import db


class TrashService:

    @staticmethod
    def get_deleted_tasks_by_date():
        today = date.today()
        yesterday = today - timedelta(days=1)

        today_deleted = Task.query.filter_by(
            deleted=True, deleted_date=today
        ).all()

        yesterday_deleted = Task.query.filter_by(
            deleted=True, deleted_date=yesterday
        ).all()

        return today_deleted, yesterday_deleted

    @staticmethod
    def bulk_restore(task_ids):
        for task_id in task_ids:
            task = Task.query.get(task_id)
            if task and task.deleted:
                task.restore()
        db.session.commit()

    @staticmethod
    def bulk_delete_permanently(task_ids):
        for task_id in task_ids:
            task = Task.query.get(task_id)
            if task:
                db.session.delete(task)
        db.session.commit()