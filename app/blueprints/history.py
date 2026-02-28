from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.history_service import HistoryService

history_bp = Blueprint("history", __name__, url_prefix="/history")


@history_bp.route("/")
def view_history():
    today_tasks, yesterday_tasks = HistoryService.get_tasks_grouped_by_date()

    return render_template(
        "tasks/history.html",
        today_tasks=today_tasks,
        yesterday_tasks=yesterday_tasks
    )


@history_bp.route("/action", methods=["POST"])
def history_action():
    action = request.form.get("action")
    task_ids = request.form.get("all_task_ids", "")

    ids = [int(i) for i in task_ids.split(",") if i.isdigit()]

    if action == "reopen":
        HistoryService.bulk_reopen(ids)
        flash(f"{len(ids)} task(s) reopened.", "success")

    elif action == "trash":
        HistoryService.bulk_move_to_trash(ids)
        flash(f"{len(ids)} task(s) moved to trash.", "success")

    return redirect(url_for("history.view_history"))