from datetime import date, timedelta
from app.models import Task
from app.extensions import db


class HistoryService:

    @staticmethod
    def get_tasks_grouped_by_date():
        today = date.today()
        yesterday = today - timedelta(days=1)

        today_tasks = Task.query.filter_by(
            completed=True, deleted=False, completed_date=today
        ).all()

        yesterday_tasks = Task.query.filter_by(
            completed=True, deleted=False, completed_date=yesterday
        ).all()

        return today_tasks, yesterday_tasks

    @staticmethod
    def bulk_reopen(task_ids):
        for task_id in task_ids:
            task = Task.query.get(task_id)
            if task:
                task.reopen()
        db.session.commit()

    @staticmethod
    def bulk_move_to_trash(task_ids):
        for task_id in task_ids:
            task = Task.query.get(task_id)
            if task:
                task.move_to_trash()
        db.session.commit()