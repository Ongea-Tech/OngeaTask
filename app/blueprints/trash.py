from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.trash_service import TrashService

trash_bp = Blueprint("trash", __name__, url_prefix="/trash")


@trash_bp.route("/")
def view_trash():
    today_deleted, yesterday_deleted = TrashService.get_deleted_tasks_by_date()

    return render_template(
        "tasks/trash.html",
        today_deleted=today_deleted,
        yesterday_deleted=yesterday_deleted
    )


@trash_bp.route("/restore", methods=["POST"])
def restore_bulk():
    task_ids = request.form.get("all_task_ids", "")
    ids = [int(i) for i in task_ids.split(",") if i.isdigit()]

    TrashService.bulk_restore(ids)
    flash(f"{len(ids)} task(s) restored.", "success")

    return redirect(url_for("trash.view_trash"))


@trash_bp.route("/delete", methods=["POST"])
def delete_permanently():
    task_ids = request.form.get("all_task_ids", "")
    ids = [int(i) for i in task_ids.split(",") if i.isdigit()]

    TrashService.bulk_delete_permanently(ids)
    flash(f"{len(ids)} task(s) permanently deleted.", "success")

    return redirect(url_for("trash.view_trash"))