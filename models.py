from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_colleague(id):
    return Colleagues.query.get(int(id))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), unique = True, index = True)
    logo = db.Column(db.String(8), nullable = True)
    create_at = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    founder_password = db.Column(db.String(128))     # to login as colleague 
    joining_password = db.Column(db.String(128))     # to invite colleagues for joining
    # one-to-many relation: company < colleagues
    colleagues = db.relationship(
        "Colleagues", 
        backref = "company", 
        lazy = "dynamic", 
        cascade = "all, delete, delete-orphan"
    )

    def __repr__(self):
        return f"""Company name: {self.name}
ID: {self.id}
Joined to Idea Box at: {self.create_at}"""

    def set_founder_password(self, founder_password):
        self.founder_password = generate_password_hash(founder_password)
    
    def check_founder_password(self, founder_password):
        return check_password_hash(self.founder_password, founder_password)
    
    def set_joining_password(self, joining_password):
        self.joining_password = generate_password_hash(joining_password)
    
    def check_joining_password(self, joining_password):
        return check_password_hash(self.joining_password, joining_password)

class Colleagues(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(32), unique = True, index = True)
    email = db.Column(db.String(128), unique = True, index = True)
    confirmed = db.Column(db.Integer, unique = False, default = 0)
    first_name = db.Column(db.String(32), nullable = False, index = True)
    last_name = db.Column(db.String(64), nullable = False, index = True)
    avatar = db.Column(db.String(8), nullable = True)
    position = db.Column(db.String(2048), index = True)
    password_hash = db.Column(db.String(128))
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    # one-to-many relation: colleague < ideas
    ideas = db.relationship(
        "Ideas", 
        backref = "colleague", 
        lazy = "dynamic", 
        cascade = "all, delete, delete-orphan"  # cascading deletion
    )
    # one-to-one relation: admin - colleague
    admin = db.relationship(
        "Admins", 
        backref = "colleague", 
        lazy = "dynamic", 
        cascade = "all, delete, delete-orphan"  # cascading deletion
    )

    def __repr__(self):
        return f"""User name: {self.user_name}
First name: {self.first_name}
Last name: {self.last_name}
ID: {self.id}
Email: {self.email}
Position: {self.position}"""

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def fullname(self):
        return f"{self.first_name} {self.last_name}"

class Admins(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    
    # privilegs to change name, logo, email, joiner password
    update_company = db.Column(db.Boolean, unique = False, default = False, index = True)
    
    # privilegs to add-remove colleagues to the admin-team with privilegs and update existed privilegs
    update_privilegs = db.Column(db.Boolean, unique = False, default = False, index = True)
    
    # privileges to register-update-delete colleagues 
    update_colleague = db.Column(db.Boolean, unique = False, default = False, index = True)
    
    # privilegs to create-update-delete idea box and post
    update_box = db.Column(db.Boolean, unique = False, default = False, index = True)
    
    colleague_id = db.Column(db.Integer, db.ForeignKey("colleagues.id"))
    
    # one-to-many relation: admin < boxes
    boxes = db.relationship(
        "Boxes", 
        backref = "admin", 
        lazy = "dynamic", 
        cascade = "all, delete, delete-orphan"
    )
    
    def __repr__(self):
        if self.colleague:
            return f"""Admin name: {self.colleague.user_name}
Admin ID: {self.id}
Colleague ID: {self.colleague.id}
Email: {self.colleague.email}
Privilegs:
    - Update Company: {self.update_company}
    - Update Privilegs: {self.update_privilegs}
    - Update Colleagues: {self.update_colleague}
    - Update Idea Box: {self.update_box}"""

        return f"""Not in admin team
"""

class Boxes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), unique = True, index = True)
    description = db.Column(db.String(16384), index = True)
    create_at = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    close_at = db.Column(db.String(128), index = True, default = datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"))
    # one-to-many relation: Boxes < ideas
    ideas = db.relationship(
        "Ideas", 
        backref = "box", 
        lazy = "dynamic", 
        cascade = "all, delete, delete-orphan"  # cascading deletion
    )

    def __repr__(self):
        return f"""Box name: {self.name}
        ID: {self.id}
        Description: {self.description}
        Created at: {self.create_at}"""

class Ideas(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    idea = db.Column(db.String(32768), index = True)
    sign = db.Column(db.String(128))
    create_at = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    box_id = db.Column(db.Integer, db.ForeignKey("boxes.id"))
    colleague_id = db.Column(db.Integer, db.ForeignKey("colleagues.id"))

    def __repr__(self):
        return f"""ID: {self.id}
Idea: {self.idea}
Sign: {self.sign}
Colleague ID: {self.colleague_id}
Box ID: {self.box_id}
Created at: {self.create_at}"""
