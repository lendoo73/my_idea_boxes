from models import Boxes, Colleagues, Admins
from models import Company, Admins
from flask_login import logout_user
from flask import flash, redirect, url_for, session
from wtforms.fields import Label     # to change dinamicly form.label text
import re                            # to clean text from HTML tags and entities
from models import Colleagues, Admins, Boxes
from app import db
import random
import os
import s3


def print_current_user(current_user):
    print(current_user)
    print("current_user.get_id(): ", current_user.get_id())
    print("current_user.is_active: ", current_user.is_active)
    print("current_user.is_anonymous: ", current_user.is_anonymous)
    print("current_user.is_authenticated: ", current_user.is_authenticated)


def get_nav(current_user, lst = ["Main"], colleague = None):
    if not colleague:
        colleague = current_user

    left = {
        "Home": "/",
        "Sample": "/sample",
        "Main": "/main",
        "Profile": "profile",
        "Company": "/company_profile",
        "Colleagues": "/colleagues",
        "Privilegs": "/privilegs"
    }

    right = {
        "Colleague": "/register",
        "Companies": "/register_company",
        "Login": "/login"
    }

    nav = {
        "left": {},
        "right": {}
    }

    for val in lst:
        if val in left:
            nav["left"][val] = left[val]
        else:
            nav["right"][val] = right[val]

    if current_user.get_id():
        nav["right"]["Logout"] = "/logout"
        nav["right"][current_user.user_name] = "/profile"
        # add admin menu:
        if is_auth_company(current_user):
            nav["left"]["Company"] = left["Company"]
        if is_auth_colleague(current_user, colleague):
            nav["left"]["Colleagues"] = left["Colleagues"]
        if is_auth_privilegs(current_user):
            nav["left"]["Privilegs"] = left["Privilegs"]

    return nav


# instatiate colleague:
def instatiate_colleague(form):
    colleague = Colleagues(
        user_name = form.user_name.data,
        email = form.email.data,
        first_name = form.first_name.data,
        last_name = form.last_name.data,
        position = form.position.data
    )

    return colleague

# create admin privilegs:


def instatiate_admin(privileg):

    admin = Admins(
        update_company = privileg,
        update_privilegs = privileg,
        update_colleague = privileg,
        update_box = privileg
    )

    return admin

# ---------------------------- Authorization ----------------------------
# get the current user admin_privilegs


def get_admin(current_user):
    admin = Admins.query.filter(Admins.colleague_id == current_user.id).first()
    if not admin:
        # if the colleague has not admin privilegs create an Admin withouth privilegs:
        admin = instatiate_admin(False)

    return admin


def get_admin_id(current_user):
    admin = Admins.query.filter(Admins.colleague_id == current_user.id).first()
    if admin:
        return admin.id


def is_auth_company(current_user):
    admin = get_admin(current_user)
    if not admin.update_company:
        return False
    return True


def is_auth_colleague(current_user, colleague=None):
    if not colleague:
        colleague = current_user
    admin = get_admin(current_user)
    if not admin.update_colleague:
        # current user is not an admin with update colleague privileg
        return False
    if current_user.company_id != colleague.company_id:
        # current user is belong to different company
        return False
    return True


def is_auth_privilegs(current_user, colleague=None):
    if not colleague:
        colleague = current_user

    admin = get_admin(current_user)
    if not admin.update_privilegs:
        return False
    if current_user.company_id != colleague.company_id:
        # current user is belong to different company
        return False
    return True


def is_auth_box(current_user):
    admin = get_admin(current_user)
    if not admin.update_box:
        return False
    return True


def unathorized(message = "You are not authorized to view this page.", category = "success"):
    # log out unauthorized colleague and redirect to login page
    logout_user()
    flash(message, category)
    return redirect(url_for("login"))


def authenticate_company(box_id, current_user):
    return bool(
        db.session.query(Boxes, Admins, Colleagues).filter(
            Boxes.id == box_id,
            Boxes.admin_id == Admins.id,
            Colleagues.id == Admins.colleague_id,
            Colleagues.company_id == current_user.company_id
        ).all()
    )

def get_avatar(current_user):
    # returns the avatar of current user
    extension = current_user.avatar
    print("current_user.avatar: ", current_user.avatar)
    print("extension: ", extension)
    if extension:
        file = f"{current_user.id}.{extension}"
        if not os.path.exists(f"static/avatars/{file}"):
            # download avatar from AWS:
            bucket = os.environ["S3_BUCKET"]
            object_name = f"avatars/{file}"
            s3.download(bucket, object_name)
        return file
    else:
        return "default.png"



def get_logo(current_user):
    # returns the logo of current company
    id = current_user.company_id
    company = Company.query.get(id)
    logo_extension = company.logo
    return f"{id}.{logo_extension}" if logo_extension else "idea-box.svg"


def get_placeholder(colleague, current_user, form):
    placeholder = "Your current password"
    if colleague.email != current_user.email:
        placeholder = "Admin password"
        form.password.label = Label(field_id="password", text=placeholder)
    return placeholder


def update_authorization(current_user, id):

    colleague = current_user
    who = "Your"
    authorized = True

    if current_user.id != id:
        # authenticate admin:
        colleague = Colleagues.query.get(id)
        who = "Colleague"
        if not is_auth_colleague(current_user) or colleague.company_id != current_user.company_id:
            return None, None, False
        # admin authorized, help colleague to update data:

    return colleague, who, authorized

def remove_html(raw_html):
    regex = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleaned = re.sub(regex, "", raw_html)
    return cleaned

def get_idea_box(box_id, current_user):
    return db.session.query(Boxes, Admins, Colleagues).filter(
        Boxes.id == box_id,
        Boxes.admin_id == Admins.id,
        Colleagues.id == Admins.colleague_id,
        Colleagues.company_id == current_user.company_id
    ).first()


def get_extension(file_name):
    return file_name.split(".")[-1].lower()


def set_confirmation_code(colleague, confirmation_email = None):
    if not confirmation_email:
        confirmation_email = colleague.email
    # save confirmation code to the database:
    code = random.randint(100000, 999999)
    colleague.confirmed = code
    try:
        session['current_email'] = colleague.email
        session['confirmation_email'] = confirmation_email
        session['logo'] = get_logo(colleague)
        db.session.commit()
        flash(f"An email sent to {confirmation_email} with a confirmation code.", "inform")
        return True
    except:
        flash(f"Any error occured. Please try again.", "error")
        db.session.rollback()
        return False

def remove_avatar_file(colleague, extension = None):
    bucket = os.environ["S3_BUCKET"]
    file = f"avatars/{colleague.id}.{extension or colleague.avatar}"
    avatar = f"static/{file}"
    # remove from Heroku:
    if os.path.exists(avatar):
        os.remove(avatar)
    # remove avatar from AWS:
    s3.delete(bucket, file)