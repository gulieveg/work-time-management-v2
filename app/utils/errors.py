from flask import Flask, render_template
from werkzeug.exceptions import NotFound


def handle_error_404(app: Flask) -> callable:
    @app.errorhandler(404)
    def page_not_found(error: NotFound) -> str:
        return render_template("errors/404.html"), 404

    return page_not_found
