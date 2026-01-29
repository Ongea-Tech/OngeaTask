from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Subtask, db 
from app.models import Task          

subtasks_bp = Blueprint("subtasks", __name__, url_prefix="/subtasks")

# View all subtasks for a task
@subtasks_bp.route("/<int:task_id>")
def list_subtasks(task_id):
    task_subtasks = Subtask.query.filter_by(task_id=task_id).all()
    return render_template("subtasks_list.html", subtasks=task_subtasks, task_id=task_id)

# Create a new subtask for a task
@subtasks_bp.route("/create/<int:task_id>", methods=["POST"])
def create_subtask(task_id):
    title = request.form.get("title")
    if not title or not title.strip():
        flash("Subtask title is required!", "error")
        return redirect(url_for("subtasks.list_subtasks", task_id=task_id))

    new_subtask = Subtask(title=title, task_id=task_id)
    db.session.add(new_subtask)
    db.session.commit()
    flash("Subtask created!", "success")
    return redirect(url_for("subtasks.list_subtasks", task_id=task_id))
