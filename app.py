from datetime import datetime
from flask import Flask, render_template, request,jsonify,redirect,session
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, storage
from firebase_admin import auth
import secrets
from datetime import datetime
import json
import requests

logistx_cred = credentials.Certificate("")
logistx = firebase_admin.initialize_app(logistx_cred,{'storageBucket': 'logistx-7b788.appspot.com'})
db= firestore.client(logistx)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route('/', methods=['GET', 'POST'])
def home():
    
    return render_template('home.html')



if __name__ == '__main__':
    app.run(debug=True)
