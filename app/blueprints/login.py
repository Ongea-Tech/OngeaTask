from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.services.login_service import LoginService

login_bp = Blueprint("login", __name__)  


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("tasks.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = LoginService.authenticate(email, password)

        if user:
            LoginService.login(user)
            flash("Welcome back!", "success")
            return redirect(url_for("tasks.dashboard"))
        else:
            flash("Invalid email or password", "error")

    return render_template("login.html")


@login_bp.route("/logout")
def logout():
    LoginService.logout()
    flash("Logged out successfully", "success")
    return redirect(url_for("login.login"))
