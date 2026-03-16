import uuid
from flask import render_template, current_app, request
from werkzeug.exceptions import HTTPException, InternalServerError
from sqlalchemy.exc import OperationalError


def register_error_handlers(app):
    @app.errorhandler(401)
    def handle_401(e):
        current_app.logger.warning(f"401 Unauthorized: path={request.path}")
        return render_template(
            "401.html",
            message="You must be logged in to access this page."
        ), 401

    @app.errorhandler(403)
    def handle_403(e):
        current_app.logger.warning(f"403 Forbidden: path={request.path}")
        return render_template(
            "403.html",
            message="You do not have permission to access this resource."
        ), 403

    @app.errorhandler(404)
    def handle_404(e):
        current_app.logger.info(f"404 Not Found: path={request.path}")
        return render_template(
            "404.html",
            message="The page or task you requested could not be found."
        ), 404

    @app.errorhandler(500)
    @app.errorhandler(InternalServerError)
    def handle_internal_server_error(e):
        request_id = str(uuid.uuid4())

        current_app.logger.error(
            f"[request_id={request_id}] 500 Internal Server Error on path={request.path}: {e}",
            exc_info=True
        )

        try:
            return render_template(
                "500.html",
                message="Something went wrong on our end. Please try again later.",
                request_id=request_id
            ), 500
        except Exception as template_error:
            current_app.logger.error(
                f"[request_id={request_id}] Failed to render 500.html: {template_error}",
                exc_info=True
            )
            return f"Fallback 500 page. Reference ID: {request_id}", 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e

        from . import db

        request_id = str(uuid.uuid4())

        try:
            db.session.rollback()
        except Exception:
            current_app.logger.warning("Rollback failed while handling exception.")

        current_app.logger.error(
            f"[request_id={request_id}] Unhandled exception on path={request.path}: {e}",
            exc_info=True
        )

        try:
            if isinstance(e, OperationalError):
                return render_template(
                    "500.html",
                    message="The system is temporarily unavailable. Please try again shortly.",
                    request_id=request_id
                ), 503

            return render_template(
                "500.html",
                message="Something went wrong on our end. Please try again later.",
                request_id=request_id
            ), 500
        except Exception as template_error:
            current_app.logger.error(
                f"[request_id={request_id}] Failed to render 500.html from exception handler: {template_error}",
                exc_info=True
            )
            return f"Fallback error page. Reference ID: {request_id}", 500