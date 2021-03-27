from app import app, db
from flask import  request, render_template, flash, redirect, url_for, session
from models import Company, Colleagues, Admins, Boxes, Ideas
from forms import RegistrationFormCompany, RegistrationFormColleague, LoginForm, ConfirmEmailForm, UpdateFirstNameForm, UpdateLastNameForm, UpdateEmailForm, UpdatePositionForm, UpdatePasswordForm, UpdateAvatarForm, allowed_format, UpdateLogoForm, UpdateCompanyNameForm, UpdateJoiningPasswordForm, DeleteColleagueForm, UpdatePrivilegsForm, CreateBoxForm, CreateIdeaForm
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from helper import print_current_user, instatiate_colleague, instatiate_admin, get_admin, get_admin_id, get_avatar, get_logo, unathorized, get_nav, get_placeholder, is_auth_company, is_auth_colleague, is_auth_privilegs, is_auth_box, update_authorization, remove_html, get_idea_box, authenticate_company, get_extension, set_confirmation_code, remove_avatar_file, remove_logo_file
from date import str_to_date, is_open
import os                        # to delete uploaded avatar
from sqlalchemy import func      # to use func in qurey
from send_email import send_email
from email_templates import confirm_email_txt, confirm_email_HTML
from add_data import del_company, create_sample_company
import sys
import s3

@app.route("/")
def landing_page():
    # create sample company if it been deleted:
    try:
        sample_company = Company.query.filter_by(name = "Eric BLABLA KGB").first()
    except:
        # initilize postgreSQL database on heroku:
        print("Unexpected error:", sys.exc_info()[0])
        print("Initialize database...")
        db.create_all()
        create_sample_company()
        return redirect(url_for("landing_page"))
    if not sample_company:
        print("Create sample company...")
        create_sample_company()
    
    if current_user.is_authenticated:
        logout_user()
    
    return render_template(
        "landing_page.html",
        nav = get_nav(current_user, ["Home", "Sample", "Login", "Colleague", "Companies"])
    )

# registration for companies
@app.route("/register_company", methods = ["GET", "POST"])
def register_company():

    if current_user.is_authenticated:
        logout_user()

    form = RegistrationFormCompany()
    
    if form.validate_on_submit():
        # instatiate Company:
        company = Company (
            name = form.company_name.data
        )
        company.set_founder_password(form.founder_password.data)
        company.set_joining_password(form.joining_password.data)
        
        # update database and query the ID of the new company:
        try:
            db.session.add(company)
            db.session.commit()
        except:
            db.session.rollback()
            flash("Any error occured when created company registration. Please try again.", "error")
            return redirect(url_for("register_company"))

        registered_company = Company.query.filter_by(name = form.company_name.data).first()

        colleague = instatiate_colleague(form)
        colleague.company_id = registered_company.id
        colleague.set_password(form.founder_password.data)
        
        # update database and register the founder as a first colleague:
        try:
            db.session.add(colleague)
            db.session.commit()
        except:
            db.session.rollback()
            flash("Any error occured when created colleague registration. Please try again.", "error")
            return redirect(url_for("register_company"))

        # set the founder as Admin with full privilegs:
        registered_colleague = Colleagues.query.filter_by(email = form.email.data).first()
        # instatiate Admins:
        admin = instatiate_admin(True)
        admin.colleague_id = registered_colleague.id
        try:
            db.session.add(admin)
            db.session.commit()
        except:
            db.session.rollback()
            flash("Any error occured when created admin registration. Please try again.", "error")
            return redirect(url_for("register_company"))
        
        flash("Congratulations, you are now registered your Company!", "inform")
        return redirect(url_for("login"))
    
    return render_template(
        "register_company.html", 
        form = form,
        nav = get_nav(current_user, ["Home", "Sample", "Login", "Colleague"])
    )

# registration for colleagues
@app.route("/register", methods = ["GET", "POST"])
def register():
    # if an admin help at registration for colleague, logout the admin:
    if current_user.is_authenticated:
        logout_user()

    form = RegistrationFormColleague()
    
    if form.validate_on_submit():
        company = Company.query.filter_by(name = form.company_name.data).first()
        if company is None or not company.check_joining_password(form.joining_password.data):
            flash(f"Invalid Company name ({form.company_name.data}) or your joining password is not valid.", "warning")
            
            return redirect(url_for("register"))
        
        # company name and joining password correct:
        colleague = instatiate_colleague(form)
        colleague.company_id = company.id
        colleague.set_password(form.password.data)

        # insert new colleague to the colleague table:
        print(colleague)
        try:
            db.session.add(colleague)
            db.session.commit()
            flash('Congratulations, you are now a registered colleague!', "inform")
        except:
            db.session.rollback()
            flash("Any error occured when created colleague registration. Please try again.", "error")
            return redirect(url_for("register"))
        
        return redirect(url_for("login"))

    return render_template(
        "register.html", 
        form = form,
        nav = get_nav(current_user, ["Home", "Sample", "Login", "Companies"])
    )

@app.route("/login", methods = ["GET", "POST"])
def login():
    #   check if current_user logged in, if so redirect to a page that makes sense
    if current_user.is_authenticated:
        # check if email already confirmed:
        colleague = Colleagues.query.get(current_user.get_id())
        if colleague.confirmed == 1:
            return redirect(url_for("main"))
    form = LoginForm()
    
    if form.validate_on_submit():
        # login with username:
        colleague = Colleagues.query.filter_by(user_name = form.email_or_user_name.data).first()
        if colleague is None:
            # login with email:
            colleague = Colleagues.query.filter_by(email = form.email_or_user_name.data).first()
        if  colleague is None or not colleague.check_password(form.password.data):
            flash("Invalid email or invalid username or misspelled password.", "warning")
            return redirect(url_for("login"))
        
        # confirm email, if required:
        if colleague.confirmed != 1:
            # save confirmation code to the database:
            if  not set_confirmation_code(colleague):
                redirect(url_for("login"))

            login_user(colleague, form.remember_me.data)
            return redirect(url_for("confirm_email"))
        
        login_user(colleague, form.remember_me.data)
        
        return redirect(url_for("main"))
    
    return render_template(
        "login.html", 
        form = form,
        nav = get_nav(current_user, ["Home", "Sample", "Login", "Colleague", "Companies"])
    )

@app.route("/confirm_email", methods = ["GET", "POST"])
def confirm_email():

    form = ConfirmEmailForm()

    if form.validate_on_submit():
        colleague = Colleagues.query.filter_by(email = form.email.data).first()
        if colleague.confirmed == form.code.data:
            # email confirmed:
            colleague.confirmed = 1
            success = ""
            error = ""
            if session['confirmation_email'] != session['current_email']:
                # refresh email:
                colleague.email = session['confirmation_email']
                success = f"{colleague.fullname()}'s email changed successfully to {colleague.email}."
                email_count = Colleagues.query.filter(Colleagues.email == session['confirmation_email']).count()
                if email_count:
                    error = f"This email ({session['confirmation_email']}) already registered."
            try:
                db.session.commit()
                flash(f"Your email confirmed successfully.", "inform")
                flash(success, "inform")
                login_user(colleague)
                return redirect(url_for("main"))
            except:
                flash(error, "error")
                flash(f"Any error occured. Please try again.", "error")
                db.session.rollback()
                return redirect(url_for("login"))
        else:
            form.code.errors.append("Confirmation code does not match.")

    form.email.data = session['current_email']
    logo = session['logo']
    if not form.code.errors:
        to = session['confirmation_email']
        subject = "Email confirmation"
        code = current_user.confirmed
        message_txt = confirm_email_txt(current_user.first_name, code)
        message_HTML = confirm_email_HTML(current_user.first_name, code)
        
        # send confirmation email to the colleague:
        send_email(to, subject, message_txt, message_HTML, logo)
        logout_user()
    else:
        form.code.errors.append("To resend confirmation email click on [Login]")


    return render_template(
        "confirm_email.html", 
        form = form,
        logo = logo,
        nav = get_nav(current_user, ["Home", "Login"])
    )

@app.route("/sample", methods = ["GET", "POST"])
def sample():
    
    sample_company = Company.query.filter_by(name = "Eric BLABLA KGB").first()
    colleagues = Colleagues.query.filter(Colleagues.company_id == sample_company.id).all()

    return render_template(
        "sample.html", 
        colleagues = colleagues,
        nav = get_nav(current_user, ["Home", "Login", "Colleague"])
    )

@app.route("/main", methods = ["GET", "POST"])
@login_required 
def main():

    company = Company.query.get(current_user.company_id)
    company_id = company.id
    get_avatar(current_user) # have to download avatar from AWS, otherwise the photo not rendered.

    # display existed Idea Boxes:
    boxes = db.session.query(Boxes, Admins, Colleagues).filter(
        Boxes.admin_id == Admins.id,
        Colleagues.id == Admins.colleague_id,
        Colleagues.company_id == company_id
    ).all()


    # replace any HTML elements and entities from the name:
    for box in boxes:
        # query the last activity from the idea table corresponding to the current box
        activity = db.session.query(func.max(Ideas.create_at)).filter(Ideas.box_id == box.Boxes.id).first()
        
        # query all ideas of the current box:
        ideas = Ideas.query.filter(Ideas.box_id == box.Boxes.id).all()
        box.Boxes.counter = len(ideas)
        
        # query the last 5 poster's avatars:
        posters = []
        for poster in ideas[-5 :]:
            data = {
                "name": poster.sign,
                "avatar": "incognito-cut.svg"
            }
            if poster.sign != "incognito":
                data["avatar"] = get_avatar(Colleagues.query.get(poster.colleague_id))
            posters.append(data)

        box.Boxes.posters = posters
        box.Boxes.activity = activity[0]
        box.Boxes.name = remove_html(box.Boxes.name)

    return render_template(
        "main.html", 
        logo = get_logo(current_user),
        change_logo = is_auth_company(current_user), # to add click event to change logo for authorized admin
        update_box = is_auth_box(current_user),      # to add edit icon to authorized admin
        boxes = boxes,
        nav = get_nav(current_user)
    )


@app.route("/profile/<int:id>", methods = ["GET", "POST"])
@login_required 
def profile(id):

    colleague = Colleagues.query.get(id)
    if current_user.id != id:
        # authenticate admin:
        if not is_auth_colleague(current_user, colleague):
            return unathorized("You cannot to view the profile of someone else.", "error")
        
        # admin authorized, view colleague's record:
        who = "Colleague"
    else:
        # colleague view itself:
        colleague = current_user
        who = "Your"

    return render_template(
        "profile.html", 
        avatar = get_avatar(colleague),
        colleague = colleague,
        nav = get_nav(current_user)
    )

@app.route("/update_first_name/<int:id>", methods = ["GET", "POST"])
@login_required 
def update_first_name(id):

    colleague, who, authorized = update_authorization(current_user, id)
    if not authorized:
        return unathorized("Only your own name can you change.", "error")

    form = UpdateFirstNameForm()
    
    
    if form.validate_on_submit():
        if colleague.first_name != form.first_name.data:
            colleague.first_name = form.first_name.data
            try:
                db.session.commit()
                flash(f"{who} Firs Name changed successfully to {colleague.first_name}.", "inform")
            except:
                flash(f"Any error occured. Please try again.", "error")
                db.session.rollback()
        
        return redirect(url_for("profile", id = id))

    return render_template(
        "update_first_name.html", 
        type = "First Name",
        value = colleague.first_name,
        form = form,
        colleague = colleague,
        avatar = get_avatar(colleague),
        nav = get_nav(current_user)
    )

@app.route("/update_last_name/<int:id>", methods = ["GET", "POST"])
@login_required 
def update_last_name(id):
    
    colleague, who, authorized = update_authorization(current_user, id)
    if not authorized:
        return unathorized("Only your own name can you change.", "error")

    form = UpdateLastNameForm()

    if form.validate_on_submit():
        if colleague.last_name != form.last_name.data:
            colleague.last_name = form.last_name.data
            try:
                db.session.commit()
                flash(f"{who} Last Name changed successfully to {colleague.last_name}.", "inform")
            except:
                flash(f"Any error occured. Please try again.", "error")
                db.session.rollback()
        
        return redirect(url_for("profile", id = id))
        
    return render_template(
        "update_last_name.html", 
        type = "Last Name",
        value = colleague.last_name,
        form = form,
        colleague = colleague,
        avatar = get_avatar(colleague),
        nav = get_nav(current_user)
    )

@app.route("/update_email/<int:id>", methods = ["GET", "POST"])
@login_required 
def update_email(id):
    
    colleague, who, authorized = update_authorization(current_user, id)
    if not authorized:
        return unathorized("Only your own email can you change.", "error")

    form = UpdateEmailForm()

    if form.validate_on_submit():
        
        if  not current_user.check_password(form.password.data):
            return unathorized("Invalid password. Please log in again.", "warning")
        
        if colleague.email != form.email.data:
            # save confirmation code to the database and send email confirmation code to the new email:
            if  not set_confirmation_code(colleague, form.email.data):
                redirect(url_for("login"))

            return redirect(url_for("confirm_email"))    
        
        return redirect(url_for("profile", id = id))

    return render_template(
        "update_email.html", 
        type = "Email",
        value = colleague.email,
        placeholder = get_placeholder(colleague, current_user, form),
        form = form,
        colleague = colleague,
        avatar = get_avatar(colleague),
        nav = get_nav(current_user)
    )

@app.route("/update_position/<int:id>", methods = ["GET", "POST"])
@login_required 
def update_position(id):
    
    colleague, who, authorized = update_authorization(current_user, id)
    if not authorized:
        return unathorized("Only your own position can you change.", "error")

    form = UpdatePositionForm()

    if form.validate_on_submit():
        if colleague.position != form.position.data:
            colleague.position = form.position.data
            try:
                db.session.commit()
                flash(f"{who} position changed successfully to {form.position.data}.", "inform")
            except:
                db.session.rollback()
                flash(f"Any error occured. Please try again.", "error")
                return redirect(url_for("update_position", id = id))
        
        return redirect(url_for("profile", id = id))
        
    return render_template(
        "update_position.html", 
        type = "Position",
        value = colleague.position,
        form = form,
        colleague = colleague,
        avatar = get_avatar(colleague),
        nav = get_nav(current_user)
    )

@app.route("/update_password/<int:id>", methods = ["GET", "POST"])
@login_required 
def update_password(id):
    
    colleague, who, authorized = update_authorization(current_user, id)
    if not authorized:
        return unathorized("Only your own password can you change.", "error")

    form = UpdatePasswordForm()

    if form.validate_on_submit():
        if  not current_user.check_password(form.password.data):
            flash("Invalid password. Please log in again.", "warning")
            logout_user()
            return redirect(url_for("login"))
        if form.password.data != form.new_password.data:
            if  form.new_password.data == form.repeat_new_password.data:
                try:
                    colleague.set_password(form.new_password.data)
                    db.session.commit()
                    flash(f"{who} password changed successfully.", "inform")

                except:
                    db.session.rollback()
                    flash(f"Any error occured. Please try again.", "error")
            else: flash(f"{who} repeat password does not match. Please try again.", "warning")
        return redirect(url_for("profile", id = id))

    return render_template(
        "update_password.html", 
        type = "Password",
        value = "********",
        form = form,
        colleague = colleague,
        placeholder = get_placeholder(colleague, current_user, form),
        avatar = get_avatar(colleague),
        nav = get_nav(current_user)
    )

@app.route("/upload_avatar/<int:id>", methods = ["GET", "POST"])
@login_required 
def upload_avatar(id):

    colleague, who, authorized = update_authorization(current_user, id)
    if not authorized:
        return unathorized("Only to your account can you upload avatar can you upload.", "error")

    form = UpdateAvatarForm()

    if form.validate_on_submit():
        filename = form.avatar.data.filename
        extension = get_extension(filename)
        # delete previous avatar:
        old_extension = colleague.avatar
        if old_extension:
            remove_avatar_file(colleague, old_extension)
        
        # update colleague avatar:
        if old_extension != extension:
            colleague.avatar = extension
        try:
            db.session.commit()
            # save new avatar on Heroku:
            new_file = f"avatars/{colleague.id}.{extension}"
            form.avatar.data.save(f"static/{new_file}")
            # upload to AWS:
            print(s3.upload(f"static/{new_file}", os.environ["S3_BUCKET"], new_file))
            flash(f"Your profile photo successfully changed.", "inform")
        except:
            db.session.rollback()
            flash(f"Any error occured. Please try again.", "error")
            
        return redirect(url_for("profile", id = id))

    return render_template(
        "update_avatar.html", 
        type = "Avatar",
        value = "",
        enctype = "multipart/form-data",
        colleague = colleague,
        form = form,
        avatar = get_avatar(colleague),
        nav = get_nav(current_user)
    )

@app.route("/remove_avatar/<int:id>", methods = ["GET"])
@login_required 
def remove_avatar(id):
    colleague, who, authorized = update_authorization(current_user, id)
    if not authorized:
        return unathorized("Cannot to remove the avatar of someone else.", "error")
    
    remove_avatar_file(colleague)

    # remove avatar
    colleague.avatar = None

    try:
        db.session.commit()
        flash(f"{who} profile photo successfully removed.", "inform")
    except:
        db.session.rollback()
        flash(f"Any error occured. Please try again.", "error")
    
    return redirect(url_for("profile", id = id))

@app.route("/delete_colleague/<int:id>", methods = ["GET", "POST"])
@login_required 
def delete_colleague(id):
    
    colleague, who, authorized = update_authorization(current_user, id)
    if not authorized:
        return unathorized("Cannot to delete the registration of someone else.", "error")

    form = DeleteColleagueForm()

    if form.validate_on_submit():
        if  not current_user.check_password(form.password.data):
            flash("Invalid password. Please log in again.", "warning")
            logout_user()
            return redirect(url_for("login"))
        # check if the colleague has update_privileg:
        has_update_privileg = is_auth_privilegs(colleague)
        if has_update_privileg:
            flash(f"{colleague.fullname()} an admin with update privilegs.\nPlease remove this privileg before delete the registration.", "warning")
            return redirect(url_for("colleagues"))

        remove_avatar_file(colleague)

        # delete colleague:
        try:
            db.session.delete(Colleagues.query.get(id))
            db.session.commit()
            flash(f"{colleague.fullname()} successfully deleted from the database.", "inform")
        except:
            db.session.rollback()
            flash(f"Any error occured. Please try again.", "error")

        if who == "Your":
            return redirect(url_for("landing_page"))
        
        return redirect(url_for("colleagues"))

    return render_template(
        "delete_colleague.html", 
        form = form,
        colleague = colleague,
        placeholder = get_placeholder(colleague, current_user, form),
        avatar = get_avatar(colleague),
        nav = get_nav(current_user)
    )

@app.route("/idea_box/<int:id>", methods = ["GET", "POST"])
@login_required 
def idea_box(id):

    # have to check if the current user belong to the same company with the idea box:
    idea_box = get_idea_box(id, current_user)

    # log out unathorized user:
    if not idea_box:
        return unathorized("You cannot to view this Idea Box.", "error")

    # authorized admin with box privileg:
    if is_auth_box(current_user):
        current_user.is_admin = True

    # set is_open property to the Boxes; If the closing time already due then cannot to share new idea
    idea_box.Boxes.is_open = is_open(idea_box.Boxes.close_at)

    # query all ideas for the choosen box:
    ideas = Ideas.query.filter(Ideas.box_id == id).all()

    for idea in ideas:
        # update ideas with the poster avatar extension:
        colleague = Colleagues.query.get(idea.colleague_id)
        idea.avatar = get_avatar(colleague)
        # change sign code to the corresponded value:
        idea.position = colleague.position

    return render_template(
        "idea_box.html", 
        update_box = is_auth_box(current_user),      # to add edit icon to authorized admin
        box = idea_box.Boxes,
        ideas = ideas,
        change_logo = is_auth_company(current_user), # to add click event to change logo for authorized admin
        logo = get_logo(current_user),
        nav = get_nav(current_user)
    )

@app.route("/create_idea/<int:box_id>/<int:idea_id>", methods = ["GET", "POST"])
@login_required 
def create_idea(box_id, idea_id):

    # if  id == 0 create new idea, otherwise update existed idea by id
    # authenticate user:
    idea_box = get_idea_box(box_id, current_user)
    
    # log out unathorized user:
        # if idea_box empty then current user belong to different company
        # if  idea box already closed the user modified the url field
    if not idea_box or not is_open(idea_box.Boxes.close_at):
        return unathorized("You cannot to edit this Idea.", "error")

    current_idea = Ideas.query.get(idea_id)
    colleague = current_user
    current_user.is_admin = False

    if idea_id > 0 and current_idea.colleague_id != current_user.id:
        # this idea belong to different colleague than the current user, check updata_box privileg:
        if not is_auth_box(current_user):
            return unathorized("You don't hane privileg to edit this Idea.", "error")
        else:
            # current user is an admin with privileg to edit/delete boxes and ideas:
            current_user.is_admin = True
            colleague = Colleagues.query.get(current_idea.colleague_id)


    form = CreateIdeaForm()
    # change sign-input's labels to the name of current user (name must be hidden for Admins!):
    form.sign.choices = [
        ("incognito", "incognito"), 
        (current_user.user_name, current_user.user_name), 
        (current_user.first_name, current_user.first_name), 
        (current_user.fullname(), current_user.fullname())
    ] if not current_user.is_admin else [(current_idea.sign, current_idea.sign)]

    if form.validate_on_submit():
        print("submitted")
        success = ""
        error = ""
        if idea_id == 0:
            # instantiate new Idea:
            idea = Ideas(
                idea = form.idea.data,
                sign = form.sign.data,
                box_id = box_id,
                colleague_id = current_user.id
            )

            db.session.add(idea)
            success = "Thank you for sharing your Idea."
            error = "Any error occured when post your Idea. Please try again."
        
        else:
            # edit existed idea:
            error = "Any error occured when edited your Idea. Please try again."
            if current_idea.idea != form.idea.data:
                current_idea.idea = form.idea.data
                success += "Your idea successfully edited.\n"
            if current_idea.sign != form.sign.data:
                current_idea.sign = form.sign.data
                success += f"Your sign changed to {current_idea.sign}.\n"
        
        try:
            db.session.commit()
            flash(success, "inform")
            return redirect(url_for("idea_box", id = box_id))
        except:
            db.session.rollback()
            flash(error, "error")
            return redirect(url_for("create_idea", box_id = box_id, idea_id = idea_id))

    if idea_id > 0:
        # edit mode:
        form.submit.label.text = "Edit my Idea" if not current_user.is_admin else f"Edit {colleague.first_name}'s Idea"
        form.idea.data = current_idea.idea
        form.sign.data = current_idea.sign
    else:
        form.sign.data = current_user.first_name     # set first name by default checked

    return render_template(
        "create_idea.html", 
        update_box = is_auth_box(current_user),      # to add edit icon to authorized admin
        box = idea_box.Boxes,
        avatar = "incognito-cut.svg" if form.sign.data == "incognito" else get_avatar(colleague),
        form = form,
        colleague = colleague,
        change_logo = is_auth_company(current_user), # to add click event to change logo for authorized admin
        logo = get_logo(current_user),
        nav = get_nav(current_user)
    )

@app.route("/delete_idea/<int:id>", methods = ["GET", "POST"])
@login_required 
def delete_idea(id):
    
    current_idea = Ideas.query.get(id)
    box = Boxes.query.get(current_idea.box_id)

    # authenticate user
    if (current_idea.colleague_id != current_user.id and not is_auth_box(current_user)) or not is_open(box.close_at):
        return unathorized("This Idea cannot to delete.", "error")

    # delete idea:
    try:
        db.session.delete(Ideas.query.get(id))
        db.session.commit()
        flash(f"This post successfully deleted from the Idea Box.", "inform")
    except:
        db.session.rollback()
        flash(f"Any error occured. Please try again.", "error")

    return redirect(url_for("idea_box", id = current_idea.box_id))

# ----------------- required admin privilegs ----------------- :
# required update_company privileg
@app.route("/upload_logo", methods = ["GET", "POST"])
@login_required
def upload_logo():
    # authenticate colleague:
    if not is_auth_company(current_user):
        return unathorized("You cannot to upload logo.", "error")

    form = UpdateLogoForm()

    if form.validate_on_submit():
        filename = form.logo.data.filename
        extension = get_extension(filename)
        # delete previous logo:
        company = Company.query.get(current_user.company_id)
        old_extension = company.logo
        if old_extension:
            remove_logo_file(company, old_extension)
        
        # update company logo:
        if old_extension != extension:
            company.logo = extension
        try:
            db.session.commit()
            # save new logo on Heroku:
            new_file = f"logo/{company.id}.{extension}"
            form.logo.data.save(f"static/{new_file}")
            # upload to AWS:
            print(s3.upload(f"static/{new_file}", os.environ["S3_BUCKET"], new_file))
            flash(f"Your company logo successfully changed.", "inform")
        except:
            db.session.rollback()
            flash(f"Any error occured. Please try again.", "error")
            
        return redirect(url_for("main"))
        
    return render_template(
        "update_logo.html", 
        type = "Company Logo",
        value = "",
        enctype = "multipart/form-data",
        form = form,
        colleague = current_user,
        logo = get_logo(current_user),
        nav = get_nav(current_user)
    )

# required update_company privileg
@app.route("/company_profile", methods = ["GET", "POST"])
@login_required 
def company_profile():
    # authenticate colleague:
    if not is_auth_company(current_user):
        return unathorized("You cannot to view this page.", "error")

    company = Company.query.get(current_user.company_id)
    company_id = company.id
    
    # get all admins of company with update_company privileg:
    company_admins = db.session.query(Colleagues, Admins).filter(
        Colleagues.id == Admins.colleague_id,
        Colleagues.company_id == company_id,
        Admins.update_company == True
    ).all()
    return render_template(
        "company_profile.html",
        logo = get_logo(current_user),
        company = company,
        company_admins = company_admins,
        nav = get_nav(current_user)
    )

# required update_company privileg
@app.route("/update_company_name", methods = ["GET", "POST"])
@login_required 
def update_company_name():
    # authenticate colleague:
    if not is_auth_company(current_user):
        return unathorized("You are not authorized to modify the company name.", "error")

    form = UpdateCompanyNameForm()

    company = Company.query.get(current_user.company_id)

    if form.validate_on_submit():
        colleague = Colleagues.query.get(current_user.id)
        if company.name != form.company_name.data:
            company.name = form.company_name.data
            try:
                db.session.commit()
                flash(f"Your Company Name changed successfully to", "inform")
                flash(f"{company.name}.", "inform")
            except:
                flash(f"Any error occured. Please try again.", "error")
                db.session.rollback()
        
        return redirect(url_for("company_profile"))

    return render_template(
        "update_company_name.html", 
        type = "Company Name",
        value = company.name,
        colleague = current_user,
        form = form,
        logo = get_logo(current_user),
        nav = get_nav(current_user)
    )

# required update_company privileg
@app.route("/update_joining_password", methods = ["GET", "POST"])
@login_required 
def update_joining_password():
    # authenticate colleague:
    if not is_auth_company(current_user):
        return unathorized("You are not authorized to modify the joining password.", "error")

    form = UpdateJoiningPasswordForm()

    if form.validate_on_submit():
        company = Company.query.get(current_user.company_id)
        if  not company.check_joining_password(form.password.data):
            flash("Invalid password. Please log in again.", "warning")
            logout_user()
            return redirect(url_for("login"))
        if form.password.data != form.new_password.data:
            if  form.new_password.data == form.repeat_new_password.data:
                try:
                    company.set_joining_password(form.new_password.data)
                    db.session.commit()
                    flash(f"The Joining password changed successfully.", "inform")

                except:
                    db.session.rollback()
                    flash(f"Any error occured. Please try again.", "error")
            else: flash(f"Your repeat password does not match. Please try again.", "warning")
        else:
            flash(f"The new joining password equal with the old one.", "inform")
        return redirect(url_for("company_profile"))

    return render_template(
        "update_joining_password.html", 
        type = "Joining Password",
        value = "",
        form = form,
        logo = get_logo(current_user),
        colleague = current_user,
        nav = get_nav(current_user)
    )

# required update_company privileg
@app.route("/delete_company", methods = ["GET", "POST"])
@login_required 
def delete_company():
    
    # authenticate colleague:
    
    if not is_auth_company(current_user):
        return unathorized("You are not authorized to delete company.", "error")
    
    del_company(current_user.company_id)

    return redirect(url_for("landing_page"))

# required update_colleague privileg
@app.route("/colleagues", methods = ["GET", "POST"])
@login_required 
def colleagues():
    # authenticate colleague:
    if not is_auth_colleague(current_user):
        return unathorized("You cannot to vew this page.", "error")

    colleagues = Colleagues.query.filter(
        Colleagues.company_id == current_user.company_id
    ).order_by(Colleagues.id).all()

    return render_template(
        "colleagues.html",
        logo = get_logo(current_user),
        change_logo = is_auth_company(current_user), # to add click event to change logo for authorized admin
        colleagues = colleagues,
        nav = get_nav(current_user)
    )

# required update_ privilegs
@app.route("/privilegs", methods = ["GET", "POST"])
@login_required 
def privilegs():

    # authenticate colleague:
    if not is_auth_privilegs(current_user):
        return unathorized("You cannot to vew this page.", "error")

    company = Company.query.get(current_user.company_id)
    company_id = company.id
    
    # get all admins of company with any privileg:
    admins = db.session.query(Colleagues, Admins).filter(
        Colleagues.id == Admins.colleague_id,
        Colleagues.company_id == company_id
    ).all()
    
    colleagues = Colleagues.query.filter(Colleagues.company_id == current_user.company_id).all()

    for admin in admins:
        for colleague in colleagues:
            if admin.Admins.colleague_id == colleague.id:
                colleagues.remove(colleague)
    

    return render_template(
        "privilegs.html",
        logo = get_logo(current_user),
        change_logo = is_auth_company(current_user), # to add click event to change logo for authorized admin
        admins = admins,
        colleagues = colleagues,
        nav = get_nav(current_user)
    )

# required update_privilegs
@app.route("/update_privilegs/<int:id>", methods = ["GET", "POST"])
@login_required 
def update_privilegs(id):
    
    colleague = Colleagues.query.get(id)
    # authenticate colleague:
    if not is_auth_privilegs(current_user, colleague):
        return unathorized("You are not authorized to modify privilegs.", "error")

    form = UpdatePrivilegsForm()
    admin_privilegs = get_admin(colleague) 

    if form.validate_on_submit():
        if  not current_user.check_password(form.password.data):
            flash("Invalid password. Please log in again.", "warning")
            logout_user()
            return redirect(url_for("login"))
        
        admin = Admins.query.filter(Admins.colleague_id == colleague.id).first()
        
        success = ""
        error = ""
        if not admin:
            # add new admin:
            admin = Admins(
                update_company = form.update_company.data,
                update_privilegs = form.update_privilegs.data,
                update_colleague = form.update_colleague.data,
                update_box = form.update_box.data,
                colleague_id = colleague.id
            )
            db.session.add(admin)
            success += f"{colleague.fullname()} added successfully to the Admin Team.\n "
            error += f"Any error occured. Please try again.\n "
        else:
            # update privilegs:
            
            if admin_privilegs.update_company != form.update_company.data:
                admin.update_company = form.update_company.data
                success += f"{colleague.fullname()} 'Update Company' privileg successfully changed to {form.update_company.data}.\n "
                error += f"Any error occured. Please try again.\n "
            
            if admin_privilegs.update_privilegs != form.update_privilegs.data:
                # get all admins of company with update_company privileg:
                privileg_admins = db.session.query(Colleagues, Admins).filter(
                    Colleagues.id == Admins.colleague_id,
                    Colleagues.company_id == current_user.company_id,
                    Admins.update_privilegs == True
                ).all()
                # check if the colleague is the last admin with update_privileg:
                if len(privileg_admins) < 2:
                    # refuse the deletion of last privileg admin:
                    flash(f"Deletion refused because You are the last admin with update_privileg.", "warning")
                    return redirect(url_for("privilegs"))


                admin.update_privilegs = form.update_privilegs.data
                success = f"{colleague.fullname()} 'Update Privilegs' privileg successfully changed to {form.update_privilegs.data}.\n "
                error = f"Any error occured. Please try again.\n "
            
            if admin_privilegs.update_colleague != form.update_colleague.data:
                admin.update_colleague = form.update_colleague.data
                success += f"{colleague.fullname()} 'Update Colleague' privileg successfully changed to {form.update_colleague.data}.\n "
                error += f"Any error occured. Please try again.\n "
            
            if admin_privilegs.update_box != form.update_box.data:
                admin.update_box = form.update_box.data
                success += f"{colleague.fullname()} 'Update Idea Box' privileg successfully changed to {form.update_box.data}.\n "
                error += f"Any error occured. Please try again.\n "
        try:
            db.session.commit()
            flash(success, "inform")
        except:
            db.session.rollback()
            flash(error, "error")
        
        # delete admin from the table if there is no privilegs:
        admin = Admins.query.filter(Admins.colleague_id == colleague.id).first()
        is_any_privileg = admin.update_company or admin.update_privilegs or admin.update_colleague or admin.update_box
        if not is_any_privileg:
            # delete admin:
            try:
                db.session.delete(admin)
                db.session.commit()
                flash(f"{colleague.fullname()} successfully deleted from the Admin team.", "inform")
            except:
                db.session.rollback()
                flash(f"Any error occured by deleting {colleague.fullname()} from the Adnin team. Please try again.", "error")

        return redirect(url_for("privilegs"))

    return render_template(
        "update_privilegs.html", 
        form = form,
        colleague = colleague,
        admin = admin_privilegs,
        avatar = get_avatar(colleague),
        nav = get_nav(current_user)
    )

# required update_box:
@app.route("/create_box/<int:id>", methods = ["GET", "POST"])
@login_required 
def create_box(id):
    # if  id == 0 create new box, otherwise update box by id
    # authenticate admin:
    if not is_auth_box(current_user):
        return unathorized("You are not authorized to create Idea Box.", "error")
    
    # authenticate company
    if id > 0 and not authenticate_company(id, current_user):
        return unathorized("You are not authorized to update Idea Box.", "error")

    
    current_box = Boxes.query.get(id)
    form = CreateBoxForm()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        close_at = form.close_at.data
        if id == 0:
            # add new Idea Box to the Boxes table:
            new_box = Boxes(
                name = name,
                description = description,
                close_at = close_at,
                admin_id = get_admin_id(current_user)
            )

            db.session.add(new_box)
            error = "Any error occured when created new Idea Box. Please try again."
            success = "New Idea Box successfully created."
        else:
            # edit box by id:
            success = ""
            if name != current_box.name:
                current_box.name = name
                success += "Title updated.\n"
            if description != current_box.description:
                current_box.description = description
                success += "Description updated.\n"
            # close_at is a date object, have to convert to string
            str_close_at = close_at.strftime("%Y-%m-%d")
            if str_close_at != current_box.close_at:
                current_box.close_at = close_at
                success += "Closing date updated.\n"
            
            error = "Any error occured when updated Idea Box. Please try again."

        try:
            db.session.commit()
            flash(success, "inform")
        except:
            db.session.rollback()
            flash(error, "error")
            return redirect(url_for("create_box", id = id))
        
        return redirect(url_for("main"))
    
    if id > 0:
        # edit mode:
        form.submit.label.text = "Edit Box"
        form.name.data = current_box.name
        form.description.data = current_box.description
        form.close_at.data = str_to_date(current_box.close_at)

    return render_template(
        "create_box.html", 
        form = form,
        id = id,
        logo = get_logo(current_user),
        change_logo = is_auth_company(current_user), # to add click event to change logo for authorized admin
        nav = get_nav(current_user)
    )

# required update_box:
@app.route("/delete_box/<int:id>", methods = ["GET", "POST"])
@login_required 
def delete_box(id):

    # authenticate admin:
    if not is_auth_box(current_user):
        return unathorized("You are not authorized to delete Idea Box.", "error")
    
    # authenticate company:
    if not authenticate_company(id, current_user):
        return unathorized("This Idea Box belong to another company. You cannot to delete.", "error")

    # delete Idea Box:
    try:
        db.session.delete(Boxes.query.get(id))
        db.session.commit()
        flash(f"Your Idea Box successfully deleted.", "inform")
    except:
        db.session.rollback()
        flash(f"Any error occured. Please try again.", "error")

    return redirect(url_for("main"))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))
