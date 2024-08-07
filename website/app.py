import datetime
import time
import os

from flask import Flask, render_template, request, jsonify, make_response, redirect
import firebase_admin
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import jwt
import requests

# Setup/Config
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "scibowlbot-edit",
    "private_key_id": os.environ["PRIVATE_KEY_ID"],
    "private_key": os.environ["PRIVATE_KEY"].replace("\\n", "\n"),
    "client_email": os.environ["CLIENT_EMAIL"],
    "client_id": os.environ["CLIENT_ID"],
    "auth_uri": os.environ["AUTH_URI"],
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ["CLIENT_X509_CERT_URL"],
    "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://scibowlbot-edit-default-rtdb.firebaseio.com/'
})
root = db.reference('/')
db_issues = root.child("errors")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

login_URL = os.environ["LOGIN_URL"]
authorized_users = list(map(int, os.environ["AUTHORIZED"].split(",")))


@app.route('/')
def page_home():
    try:
        decoded = jwt.decode(request.cookies["token"], os.getenv("JWT_SECRET"), "HS256")
    except:
        return render_template("edit.html", title="Homepage", login=login_URL)
    else:
        return render_template("edit.html", title="Homepage", data=decoded)


@app.route("/login")
def page_login():
    return render_template("login.html")

@app.route("/suggestions", defaults={"suggestion_id": None})
@app.route("/suggestions/", defaults={"suggestion_id": None})
@app.route("/suggestions/<string:suggestion_id>")
def page_suggestions(suggestion_id):
    try:
        decoded = jwt.decode(request.cookies["token"], os.getenv("JWT_SECRET"), "HS256")
    except:
        return render_template("suggestions.html", title="Homepage", login=login_URL, issues={}, suggestion=None)

    if int(decoded["id"]) not in authorized_users:
        return render_template("suggestions.html", title="Homepage", data=decoded, authorized=False, issues={}, suggestion=None)

    suggestions = sort(dict(db_issues.get()), key=lambda x: x[1]["filed"], reverse=True)
    return render_template("suggestions.html", title="Homepage", data=decoded, authorized=True, issues=suggestions, suggestion=suggestion_id if suggestion_id else "")


@app.route("/suggestions/api/toggle_status", methods=["POST"])
def api_toggle_status():
    try:
        decoded = jwt.decode(request.cookies["token"], os.getenv("JWT_SECRET"), "HS256")
    except:
        return "You are not authorized to access this API endpoint", 401

    if int(decoded["id"]) not in authorized_users:
        return "You are not authorized to access this API endpoint", 401

    target = request.get_json().get("target", None)

    if not target:
        return "Missing required parameter: 'target'", 400

    if target not in db_issues.get():
        return f"The target '{target}' does not exist.", 400

    try:
        db_issues.child(target).child("open").set(not db_issues.child(target).child("open").get())
    except:
        return "Something went wrong", 500

    return "Success", 200

@app.route("/suggestions/api/add_discussion", methods=["POST"])
def api_add_discussion():
    try:
        decoded = jwt.decode(request.cookies["token"], os.getenv("JWT_SECRET"), "HS256")
    except:
        return "You are not authorized to access this API endpoint", 401

    if int(decoded["id"]) not in authorized_users:
        return "You are not authorized to access this API endpoint", 401

    id = request.get_json().get("id", None)
    user_id = request.get_json().get("user_id", None)
    name = request.get_json().get("name", None)
    avatar = request.get_json().get("avatar", None)
    sent = int(datetime.datetime.timestamp(datetime.datetime.now()))
    message = request.get_json().get("message", None)

    if not id or not name or not avatar or not message or not user_id:
        return "Missing one or more of the following required parameters: id, name, avatar, user_id, or message", 400

    if id not in db_issues.get():
        return f"The target '{id}' does not exist.", 400

    encoded = {
        "name": name,
        "avatar": avatar,
        "message": message,
        "id": user_id,
        "time": sent
    }

    ref = db_issues.child(id).child("discussion")
    arr: list = ref.get()
    arr.append(encoded)
    ref.set(arr)

    return jsonify(encoded), 200


@app.route("/login_get_token")
def api_login_get_token():
    key = request.args.get('access_token')

    user_info = requests.get("https://discord.com/api/users/@me", headers={
        "authorization": f"Bearer {key}"
    })

    if user_info.status_code != 200:
        return "Something Went Wrong"

    token = jwt.encode(user_info.json(), key=os.getenv("JWT_SECRET"), algorithm="HS256")

    res = make_response(redirect("/"), 200)
    res.set_cookie("token", token)

    return res


def get_avatar_link(data):
    if data["avatar"]:
        return f'https://cdn.discordapp.com/avatars/{ data["id"] }/{ data["avatar"] }.png'
    else:
        if int(data["discriminator"]) != 0:
            return f'https://cdn.discordapp.com/embed/avatars/{int(data["discriminator"]) % 5}.png'
        else:
            return f'https://cdn.discordapp.com/embed/avatars/{(int(data["id"]) >> 22) % 6}.png'


def sort(obj: dict, **options):
    return {k:v for (k, v) in sorted(obj.items(), **options)}


def format_date(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime("%m/%d/%Y %I:%M %p")


app.jinja_env.globals.update(get_avatar_link=get_avatar_link, format_date=format_date, str=str, list=list)
