from flask import request, abort
from app import app


@app.route("/")
@app.route("/index")
def index():
    print(f"index request args: {request.args}")
    abort(404)


@app.route("/get_profile.php")
def get_profile():
    print(f"get_profile req args: {request.args}")
    return "get"


@app.route("/set_profile.php")
def set_profile():
    return "set"
