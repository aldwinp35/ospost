import os
import requests
from time import sleep
from shutil import copy2
from functools import wraps
from flask import redirect, render_template, session

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

def error_template(title, msg, status_code):
    error_detail = {"title": title.title(), "msg": msg.capitalize(), "code": status_code}
    return render_template("error.html", error_detail=error_detail), error_detail["code"]


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def http_request(url, type, data=None):
    try:
        if type.upper() == "POST":
            if data == None:
                response = requests.post(url)
            else:
                response = requests.post(url, data)
        else:
            response = requests.get(url)

        response.raise_for_status()
    except requests.RequestException as e:
        print(e)
        return None

    try:
        return response.json()
    except Exception as e:
        return e


# https://flask.palletsprojects.com/en/2.1.x/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def publish_post(post_id):

    # Dont try to post on instagram on development mode
    if os.environ.get("FLASK_ENV") == "development":
        print("Your post would be publishing on instagram right now...")
        return True

    from models import db, Post, User
    from app import app
    with app.test_request_context():
        post = Post.query.filter(Post.id == post_id).first()
        if not post:
            print("No post was found")
            return None

        user = User.query.filter(User.id == post.user_id).first()
        if not user:
            print("No user was found")
            return None

        # Move image to static/tmp/ directory
        src = os.path.join("uploads", user.ig_account_id, post.filename)
        dst = "static/tmp/"

        # Create destination directory
        if not os.path.exists(dst):
            os.mkdir(dst)

        # Move img to tmp/
        try:
            copy2(src, dst)
        except Exception as e:
            return None

        # Image url
        image_url = os.getenv("APP_URL") + os.path.join(dst, post.filename)

        # Get facebook endpoint
        fb_endpoint = os.getenv("FB_ENDPOINT")

        # Create IG Container ID
        url = f"{fb_endpoint}{user.ig_account_id}/media?image_url={image_url}&caption={post.caption}&access_token={user.access_token}"
        response = http_request(url, "POST")
        if response is None:
            return None

        container_id = response["id"]

        # Check container status
        url = f"https://graph.facebook.com/{container_id}?fields=status_code&access_token={user.access_token}"
        status = "IN_PROGRESS"
        try_index = 1
        try_times = 10
        wait_time = 4
        while (status != "FINISHED"):
            if try_index == try_times:
                return None

            response = http_request(url, "get")
            if response is None:
                return None

            status = response["status_code"]
            try_index += 1
            sleep(wait_time)

        # Publish Container
        url = f"{fb_endpoint}{user.ig_account_id}/media_publish?creation_id={container_id}&access_token={user.access_token}"
        response = http_request(url, "POST")
        if response is None:
            return None

        ig_media_id = response["id"]

        if ig_media_id:
            print("media was published")
            try:
                # Delete media from static
                os.unlink(os.path.join(dst, post.filename))

                # Delete media from upload directory
                resource_path = os.path.join(app.config["UPLOAD_FOLDER_RELATIVE"], user.ig_account_id)
                os.unlink(os.path.join(resource_path, post.filename))
            except OSError as e:
                return None

            # Delete post form database
            db.session.delete(post)
            db.session.commit()

            return True
        else:
            print("Fail to post media")
            # Send an email to user

            return False
