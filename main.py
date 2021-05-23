import base64
import json, os
from flask_wtf.csrf import CSRFProtect
# MIT License
#
# Copyright (c) 2018 Real Python
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import hashlib
from google.cloud import storage
from google.cloud import datastore
from flask import redirect, request, url_for, Flask, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    UserMixin,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
import google.auth
credentials, project = google.auth.default()
#storage_client = storage.Client()

users = {}

class User(UserMixin):
    def __init__(self, id_, email):
        self.id = id_
        self.email = email
    @staticmethod
    def get(user_id):
        return users.get(user_id)
    @staticmethod
    def create(user_id, user):
        users[user_id] = user
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
UPLOAD_BUCKET = os.environ.get("UPLOAD_BUCKET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
app = Flask(__name__)
login_manager = LoginManager()
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
csrf = CSRFProtect()
csrf.init_app(app)
# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager.init_app(app)
app.config.update(
    GOOGLE_STORAGE_LOCAL_DEST = app.instance_path,
    GOOGLE_STORAGE_FILES_BUCKET=UPLOAD_BUCKET
)


@login_manager.user_loader
def load_user(user_id):
        print(users)
        return User.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", current_user=current_user)
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/login")
def login():
    print(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    print(token_response.text)

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = User(id_=unique_id, email=users_email)

    if not User.get(unique_id):
        User.create(unique_id, user)
    print(User.get(unique_id))
    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


def put_entity_to_datastore(b64_hash, email, filename):
    ds = datastore.Client()
    entity = datastore.Entity(key=ds.key('text_from_images'))
    entity.update({
        'email': email,
        'file_name': filename,
        'hash': b64_hash,
    })
    ds.put(entity)
    pass


@app.route("/upload", methods=['POST'])
@login_required
def upload():
    # retrieve data from form
    email = request.form['email']
    image = request.files['filename']
    filename = request.files['filename'].filename
    # create client that will connect to bucket
    client = storage.Client()
    bucket = client.get_bucket(UPLOAD_BUCKET)
    b64_hash = getMd5(image)
    sentinel = object()
    iterEntry = iter(find_in_storage(b64_hash))
    print(iterEntry)
    try:
        entry = iterEntry.__next__()
        print("There is already item with such md5 hash in the database")
        return render_template('already_exists.html', entry=entry)
    except google.api_core.exceptions.FailedPrecondition:
        blob = bucket.blob(b64_hash)
        image.seek(0)
        print(blob)
        print("adding entry to database")
        put_entity_to_datastore(b64_hash, email, filename)
        print("entry added to database")
        # add user email inside metadata
        blob.metadata = {'email': email}
        blob.upload_from_file(image)
        blob.reload()
        print("blob uploaded")
        print(f"blob metadata: {blob.metadata}")
        print(f"upload button clicked with form {request.form}")
        return render_template('sucesfully_added.html')

def find_in_storage(b64_hash):
    ds = datastore.Client()
    qresult = ds.query(kind="text_from_images").add_filter("hash", "=", b64_hash).fetch()
    #qresult = ds.query(kind="text_from_images").fetch()
    return qresult
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

def getMd5(f):
    f.seek(0)
    m = hashlib.md5()
    line = f.read()
    m.update(line)
    md5code = base64.b64encode(m.digest())
    #md5code = m.hexdigest()
    return md5code

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


if __name__ == "__main__":
    app.run(ssl_context='adhoc')