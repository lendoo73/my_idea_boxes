from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField, RadioField, HiddenField
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from models import Colleagues, Admins, Boxes, Ideas

class RegistrationFormCompany(FlaskForm):
    company_name = StringField("Company name", validators = [DataRequired()])
    user_name = StringField("Your User name", validators = [DataRequired()])
    first_name = StringField("Your First name", validators = [DataRequired()])
    last_name = StringField("Your Last name", validators = [DataRequired()])
    position = StringField("Your Position", validators = [DataRequired()])
    email = StringField("Email", validators = [DataRequired(), Email()])
    founder_password = PasswordField("Your own Password", validators = [DataRequired()])
    repeat_founder_password = PasswordField(
        "Repeat Your Password", 
        validators = [DataRequired(), 
        EqualTo("founder_password")]
    )
    joining_password = PasswordField("Password for Colleagues to Joining", validators = [DataRequired()])
    repeat_joining_password = PasswordField(
        "Repeat Joining Password", 
        validators = [DataRequired(), 
        EqualTo("joining_password")]
    )
    submit = SubmitField("Register your Company")

class RegistrationFormColleague(FlaskForm):
    company_name = StringField("Company name", validators = [DataRequired()])
    joining_password = PasswordField("Password for Colleagues to Joining", validators = [DataRequired()])
    user_name = StringField("Your User name", validators = [DataRequired()])
    email = StringField("Email", validators = [DataRequired(), Email()])
    first_name = StringField("Your First name", validators = [DataRequired()])
    last_name = StringField("Your Last name", validators = [DataRequired()])
    position = StringField("Your Position", validators = [DataRequired()])
    password = PasswordField("Your Password", validators = [DataRequired()])
    repeat_password = PasswordField(
        "Repeat Password", 
        validators = [DataRequired(), 
        EqualTo("password")]
    )
    
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email_or_user_name = StringField("Email or User name", validators = [DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class ConfirmEmailForm(FlaskForm):
    email = HiddenField("Email")
    code = IntegerField(
        "Confirmation code", 
        validators = [
            DataRequired(),
            NumberRange(
                min = 100000,
                max = 999999,
                message = "Please enter the 6 digits you received in the email."
            )
        ]
    )
    submit = SubmitField("Confirm my Email")

class UpdateFirstNameForm(FlaskForm):
    first_name = StringField("First Name", validators = [DataRequired()])
    submit = SubmitField("Update")

class UpdateLastNameForm(FlaskForm):
    last_name = StringField("Last Name", validators = [DataRequired()])
    submit = SubmitField("Update")

class UpdateEmailForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Update")

class UpdatePositionForm(FlaskForm):
    position = StringField("Your Position", validators = [DataRequired()])
    submit = SubmitField("Update")

class UpdatePasswordForm(FlaskForm):
    password = PasswordField("Your Current Password", validators = [DataRequired()])
    new_password = PasswordField("Your New Password", validators = [DataRequired()])
    repeat_new_password = PasswordField(
        "Repeat your New Password", 
        validators = [DataRequired(), 
        EqualTo("repeat_new_password")]
    )
    
    submit = SubmitField("Update")

allowed_format = ['png', 'svg', 'jpg', "jpeg"]
class UpdateAvatarForm(FlaskForm):
    avatar = FileField(
        "Choose an Avatar:", 
        validators = [
            FileRequired(),
            FileAllowed(allowed_format, f"Wrong format! Allowed: {allowed_format}.")
        ]
    )
    submit = SubmitField("Upload Avatar")

class DeleteColleagueForm(FlaskForm):
    password = PasswordField("Your Password", validators = [DataRequired()])
    submit = SubmitField("Delete Registration")

class UpdateLogoForm(FlaskForm):
    logo = FileField(
        "Choose your Company Logo:", 
        validators = [
            FileRequired(),
            FileAllowed(allowed_format, f"Wrong format! Allowed: {allowed_format}.")
        ]
    )
    submit = SubmitField("Upload Logo")

class UpdateCompanyNameForm(FlaskForm):
    company_name = StringField("Company Name", validators = [DataRequired()])
    submit = SubmitField("Update")

class UpdateJoiningPasswordForm(FlaskForm):
    password = PasswordField("Current Joining Password", validators = [DataRequired()])
    new_password = PasswordField("New Joining Password", validators = [DataRequired()])
    repeat_new_password = PasswordField(
        "Repeat New Password", 
        validators = [DataRequired(), 
        EqualTo("repeat_new_password")]
    )
    
    submit = SubmitField("Update")

class UpdatePrivilegsForm(FlaskForm):
    update_company = BooleanField("Update Company")
    update_privilegs = BooleanField("Update Privilegs")
    update_colleague = BooleanField("Update Colleague")
    update_box = BooleanField("Update Idea Box")
    password = PasswordField("Your Password", validators = [DataRequired()])
    submit = SubmitField("Update Privilegs")

class CreateBoxForm(FlaskForm):
    name = StringField("Title", validators = [DataRequired()])
    description = TextAreaField("Description", validators = [DataRequired()])
    close_at = DateField("Close at", format = "%Y-%m-%d")
    submit = SubmitField("Create Box")

class CreateIdeaForm(FlaskForm):
    idea = TextAreaField("My Idea", validators= [DataRequired()])
    sign = RadioField(
        "Sign", 
        choices = [
            ("incognito", "incognito"),
            ("username", "username"),
            ("first name", "first name"), 
            ("full name", "full name")
        ]
    )
    submit = SubmitField("Share my Idea")