import datetime
import math
import os
import re
import string
import time
import urllib.parse

from flask import Flask, render_template, request, jsonify, make_response, redirect
import firebase_admin
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import jwt

# Setup/Config
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "scibowlbot-edit",
    "private_key_id": "d804e81f777555f5dab10d9ee80ac56e07c9baa1",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDgaagIxMxTEp07\nT6Up7XI0rqAVluyJe3GVkMl2XuCdiijtcocT80LwszNh8GpQEcOFkY8Gx7GSDKC3\nSNaxv3LfxCERHYUoBjrOqQdDnn4Oe0rVXVw7+Xa06rf3u8I6AItAuqBsfFUnTS1b\nYJjNRctNThdhvf3gHlruFZ/bEsgMOADEo4jBgFcd5u+1p95G8SKA/VWX3NX9Ft2n\nXvU2fs6WhA6qYyYVVTBOmdLNHisGvHMFhtPIF/szoZw1Tv4Kf9tpiXJPdYmJPJWZ\nvzJvTpCddhFG+TUyJDFyuwRxQwFcitD5lg091ytYCWBZrEGRt0yg6Ra0kvaFkq6A\n4arbvr95AgMBAAECggEACIkkRc8ceXVuCxU8skNQkn3o42FV9mW+XILBEvJJZ1yb\nsWpnhmP8khSy2eEP3iNK1VADyW17jNNTop0P43tldmrqmhDOIYdZIcaums0SvODG\nKCbwrOxQblG2NSNMYDHomgnvM6koAQJvvPfH4BjtQm+7tnFIUIe/DCrA5Y+JkeNW\nKZM+rQ0Ds2bc8NRCNZ3h2+YOWgk6Qe3uPHIZJSLyQ7NOigIYDFFmUxYgBw/VrMeX\nlR4dwLlQPXm8KkIDGamkn2fwu06iD/pQlLR02UxrGzx6EAx4rugBfaVCJqQVAcQa\nf4aZA/QtDI+QClxTOfyh0lZR8WnQK38ujkvKzVJlgQKBgQD+1Qzu5h4nY1xe4ZOF\nQiEssnOYMJxtRa5j8Lrw+ChO3lMzNLkcRg99G04ypmzWzQU3memc3nOF3snTCVJX\nH5C1iBwD1b05DLQLafAfdE8zsOfrETrzeZcHBJVtoW2AhS0dkJqJvpt1nX5xm4aO\n+2QldPX9LK/MHKj/k7jflrTfwQKBgQDhcOuIMDFAMdF4FY32ssx4kElFcVv0CRxO\n2YyeKdccx97hOs4AoJNm5bZeRucRJuuYsyX+4bpWLy5YfMQoONTG1CW1agv5pOFr\nMhcPTvoVdMZ/6fLdk9FKZ7PfRodcWQlOs5u30PYHc6tzpEFqxPbSWK+FflyLwt2c\nZEdcurxNuQKBgEnBL/UU9TVBNMLhVukCssdU/s/VgfC+cjLKwdBsgn4RKtNvNwRP\n4ru6428Va/rfa9sj2NFmMNlWGePSltpQcHmZ40HY4uNYIeQLzUvNRf8X/Ie0fPNr\nBaMqWHVae27vHJep+pBTcnsgEjCfatqHN/z/VRLplBfnU6JlBuTvoXoBAoGBALcv\nb2PRbSOxl3kRYrLUZMuOyssPqt1oTcVQhy+55d6wFk5D30KpOD1DaWXADWBllMkW\nwUgUGbqQSgODFk1sqJELr7xy+FoZfUYChLRew12N7wHfkwYzZ7wi+gjyoWkLvEFk\nNqMtu80gU2/7R2C/vaP8hltd60txw2uiHE6gOgSZAoGAKmr+g/bv4YoTIqYHZw9q\nYA3uEEqKdquM6N/fkz5ClUpGV6Is6zlZcueIzH5GlryJezBScTFpcBijIrw6ureT\nkONuk3zMWJEmLBslNnR/h20bNnpu1tIwEx30PDF6ZlcYJ2iyoHCrfkr7n5ntrJ71\nQepePoH5LKa3JuZqMtkx6ec=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-1b1vf@scibowlbot-edit.iam.gserviceaccount.com",
    "client_id": "110206234798614625803",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-1b1vf%40scibowlbot-edit.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://logle-e6f2a-default-rtdb.firebaseio.com/'
})
root = db.reference('/')
db_password = root.child("passwords")
db_games = root.child("games")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route('/')
def page_home():
    try:
        decoded = jwt.decode(request.cookies["token"], os.getenv("JWTSECRET"), "HS256")
    except:
        return render_template("edit.html", title="Homepage", uname="")
    else:
        return render_template("edit.html", title="Homepage", uname=decoded['uname'])
