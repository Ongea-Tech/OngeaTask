 # app/services/individual_task_service.py

from app.models import Task, Subtask
from app.extensions import db
from flask import abort


# -------------------------------
# FETCH DATA FOR INDIVIDUAL TASK
# -------------------------------

def get_individual_task(task_id):
    """
    Fetch a single task and its subtasks.
    Used when rendering individual-task.html
    """
    task = Task.query.get(task_id)

    if not task:
        abort(404, description="Task not found")

    subtasks = Subtask.query.filter_by(task_id=task_id).all()

    return task, subtasks


# -------------------------------
# CREATE SUBTASK UNDER A TASK
# -------------------------------

def create_subtask(task_id, title):
    """
    Create a subtask for a given task
    """
    if not title or title.strip() == "":
        raise ValueError("Subtask title cannot be empty")

    task = Task.query.get(task_id)
    if not task:
        abort(404, description="Task not found")

    subtask = Subtask(
        title=title.strip(),
        task_id=task_id,
        completed=False
    )

    db.session.add(subtask)
    db.session.commit()

    return subtask


# -------------------------------
# TOGGLE SUBTASK COMPLETION
# -------------------------------

def toggle_subtask(subtask_id):
    """
    Toggle completed state of a subtask
    """
    subtask = Subtask.query.get(subtask_id)

    if not subtask:
        abort(404, description="Subtask not found")

    subtask.completed = not subtask.completed
    db.session.commit()

    update_task_completion(subtask.task_id)

    return subtask


# -------------------------------
# UPDATE TASK COMPLETION STATUS
# -------------------------------

def update_task_completion(task_id):
    """
    Mark task as completed if all subtasks are completed
    """
    task = Task.query.get(task_id)
    if not task:
        return

    subtasks = Subtask.query.filter_by(task_id=task_id).all()

    if not subtasks:
        task.completed = False
    else:
        task.completed = all(st.completed for st in subtasks)

    db.session.commit()


# -------------------------------
# DELETE A SUBTASK
# -------------------------------

def delete_subtask(subtask_id):
    """
    Delete a subtask and update task completion
    """
    subtask = Subtask.query.get(subtask_id)

    if not subtask:
        abort(404, description="Subtask not found")

    task_id = subtask.task_id

    db.session.delete(subtask)
    db.session.commit()

    update_task_completion(task_id)


# -------------------------------
# TASK PROGRESS (FOR UI)
# -------------------------------

def get_task_progress(task, subtasks):
    if subtasks is None:
        subtasks = []
        
    total = len(subtasks)
    completed = len([s for s in subtasks if s.completed])

    percent = int((completed / total) * 100) if total > 0 else 0

    if percent == 0:
        status = "Not Started"
    elif percent < 100:
        status = "In Progress"
    else:
        status = "Completed"

    return {
        "percent": percent,
        "status": status

    }

