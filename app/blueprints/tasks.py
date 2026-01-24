from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.task_service import TaskService
from app.models.task import Task  # if you still need Task for reads

bp = Blueprint("tasks", __name__)
svc = TaskService()  

@bp.post("/create_task")
def create_task():
    try:
        t = svc.create(
            title=request.form.get("name"),
            description=request.form.get("description"),
        )
        flash("Task created successfully", "success")
        return redirect(url_for("routes.show_task", task_id=t.id))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("bp.create_task"))

@bp.get("/create_task")
def create_task_form():
    return render_template("index.html")


