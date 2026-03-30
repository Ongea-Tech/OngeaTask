import uuid
from flask import render_template, current_app, request
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import OperationalError

from app.exceptions import AppException
from app.errors import ErrorCodes



def register_error_handlers(app):
    @app.errorhandler(AppException)
    def handle_app_exception(e: AppException):
        template_name = f"{e.status_code}.html"
        return render_template(
            template_name,
            message=e.message,
            details=e.details
        ), e.status_code

    @app.errorhandler(404)
    def handle_404(e):
        current_app.logger.info(
        f"404 Not Found: path={request.path}"
        )

        return render_template(
            "404.html",
            message="The page or task you requested could not be found."
        ), 404 
    
    @app.errorhandler(401)
    def handle_401(e):
        return render_template(
            "401.html",
            message="You must be logged in to view this page."
        ), 401


    @app.errorhandler(403)
    def handle_403(e):
        return render_template(
            "403.html",
            message="You do not have permission to access this page."
        ), 403
    
    
    @app.errorhandler(Exception)
    def handle_unexpected_exception(e):
        if isinstance(e, HTTPException):
            return e
        
        from . import db
        db.session.rollback()

        request_id = str(uuid.uuid4())

        current_app.logger.error(
            f"[request_id={request_id}] Unhandled exception on "
            f"{request.method} {request.path}: {type(e).__name__}: {e}",
            exc_info=True
        )

        if isinstance(e, OperationalError):
            return render_template(
                "500.html",
                message="The system is temporarily unavailable. Please try again shortly.",
                request_id=request_id
            ), 503

        return render_template(
            "500.html",
            message="Something went wrong. Please try again.",
            request_id=request_id
        ), 500