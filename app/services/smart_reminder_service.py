from datetime import datetime, timedelta, timezone
from collections import Counter

from app import db
from app.models import Task, Notification

PRIORITY_WEIGHTS = {
    "Low":1, 
    "Medium":2, 
    "High":3
    }

def get_best_completion_hour(user_id):
    completed_tasks = Task.query.filter(Task.user_id == user_id, Task.completed == True, Task.completed_at.isnot(None)).all()

    if not completed_tasks:
        return None
    completion_hours = [
        task.completed_at.hour
        for task in completed_tasks
        ]
    most_common_hour = Counter(completion_hours).most_common(1)[0][0]
    return most_common_hour

def format_hour(hour):
    if hour is None:
        return None
    if hour == 0:
        return "12 AM"
    if hour <12:
        return f"{hour} AM"
    if hour == 12:
        return "12 PM"
    elif hour >12:
        return f"{hour - 12} PM"
    
def get_best_time_message(user_id):
    best_hour = get_best_completion_hour(user_id)

    if best_hour is None:
        return "Start Completing tasks and I'll Learn your best productivity time."
    
    readable_hour = format_hour(best_hour)

    return f"You Usually Complete tasks around {readable_hour}.This may be a good time to work on an important task."

def calculate_urgency_score(task):
    score = 0

    priority = task.priority or "Medium"
    score += PRIORITY_WEIGHTS.get(priority, 2) * 10

    now = datetime.now(timezone.utc)

    if task.due_date:
        time_until_due = task.due_date - now
        days_until_due = time_until_due.days

        if task.due_date < now:
            score+= 50
        elif days_until_due == 0:
            score += 30
        elif days_until_due == 1:
            score += 20
        elif days_until_due <=3:
            score += 10

    if task.estimated_minutes:
        if task.estimated_minutes <= 30:
            score += 5
        if task.estimated_minutes >=120:
            score += 10

    return score                         

def get_task_nudge_message(task, user_id):
    best_hour = get_best_completion_hour(user_id)
    readable_hour = format_hour(best_hour)
    now = datetime.now(timezone.utc)

    if task.due_date and task.due_date < now:
        return f"'{task.title}' is overdue. This would be a good task to focus on next."
    if task.due_date and task.due_date.date() == now.date():
        return f"'{task.title}' is due today. Try making progress on it soon."
    if task.priority == "High":
        return f"'{task.title}' is marked as high priority. Consider working on it before low priority tasks."
    if readable_hour:
        return f"You usually complete tasks around {readable_hour}. This may be a good time to work on '{task.title}'."
    return f"Consider making progress on '{task.title}' today." 

def should_nudge_task(task):
    if task.completed or task.deleted:
        return False
    now = datetime.now(timezone.utc)

    if task.last_nudged_at:
        hours_since_last_nudge = (now - task.last_nudged_at).total_seconds()/3600
        if hours_since_last_nudge < 6:
            return False
        
    score = calculate_urgency_score(task)
    return score >= 25
    
def generate_smart_nudges_for_user(user_id):
    active_tasks = Task.get_active_tasks(user_id)

    if not active_tasks:
        return[]
    tasks_with_scores = [
        (task, calculate_urgency_score(task))
        for task in active_tasks
        ]
    tasks_with_scores.sort(key=lambda item: item[1], reverse=True)
    generated_notifications = []

    for task, score in tasks_with_scores[:3]:
        if should_nudge_task(task):
            message = get_task_nudge_message(task, user_id)
            notification = Notification(user_id=user_id, task_id=task.id, message=message, nudge_type="smart_reminder")
            task.last_nudged_at = datetime.now(timezone.utc)
            db.session.add(notification)
            generated_notifications.append(notification)

    db.session.commit()
    return generated_notifications

