from flask import Blueprint, render_template

help_bp: Blueprint = Blueprint("help", __name__)


@help_bp.route("/help")
def index():
    return render_template("help/index.html")


@help_bp.route("/help/tasks")
def tasks():
    return render_template("help/tasks.html")


@help_bp.route("/help/control")
def control():
    return render_template("help/control.html")