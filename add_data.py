from app import db
from models import Company, Colleagues, Admins, Boxes, Ideas
from flask import flash, redirect, url_for
from helper import instatiate_admin, get_extension, remove_avatar_file, remove_logo_file
import os
import shutil # to copy files
import random
import lorem
from date import today, add_day, str_to_date
from sqlalchemy.exc import SQLAlchemyError
import s3

def del_company(id):

    company = Company.query.get(id)

    # delete company logo:
    remove_logo_file(company, company.logo)
    
    # delete all avatars:
    colleagues = Colleagues.query.filter_by(company_id = id).all()
    for colleague in colleagues:
        remove_avatar_file(colleague)

    # delete company:
    try:
        db.session.delete(Company.query.get(id))
        db.session.commit()
        flash(f"{company.name} company successfully deleted from the database.", "inform")
    except:
        db.session.rollback()
        flash(f"Any error occured. Please try again.")

def create_sample_company():
    # instatiate Company:
    company = Company (
        name = "Eric BLABLA KGB"
    )
    company.set_founder_password("aaa")
    company.set_joining_password("bbb")
    
    # update database and query the ID of the new company:
    try:
        db.session.add(company)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Any error occured when created the sample company registration. Please try again.", "error")
        return redirect(url_for("register_company"))
    
    registered_company = Company.query.filter_by(name = "Eric BLABLA KGB").first()

    # instatiate Jhon Do:
    colleague = Colleagues(
        user_name = "jhon_do",
        email = "jhon.do@dodo.do",
        first_name = "Jhon",
        last_name = "Do",
        position = "Founder",
        confirmed = 1
    )

    colleague.set_password("aaa")
    
    data = {
        "company_id": registered_company.id,
        "colleague": colleague,
        "sample_avatar": "john_do.jpg"
    }
    
    create_sample_colleague(data)
    
    # set the founder as Admin with full privilegs:
    registered_colleague = Colleagues.query.filter_by(email = "jhon.do@dodo.do").first()
    # instatiate Admins:
    admin = instatiate_admin(True)
    admin.colleague_id = registered_colleague.id
    try:
        db.session.add(admin)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Any error occured when created sample admin registration. Please try again.", "error")
        return redirect(url_for("register_company"))
    
    # copy logo:
    location = "static/sample_logo/blabla.png"
    destination = f"static/logo/{registered_colleague.company_id}.png"
    shutil.copy2(location, destination)

    # update database:
    company.logo = "png"
    try:
        db.session.commit()
        print("Company logo copied.")
    except:
        db.session.rollback()
        print("An error occured when copied logo.")

    # instatiate Jane Do:
    colleague = Colleagues(
        user_name = "jane_do",
        email = "jane.do@dodo.do",
        first_name = "Jane",
        last_name = "Do",
        position = "Co-Founder",
        confirmed = 1
    )
    colleague.set_password("aaa")
    data = {
        "company_id": registered_company.id,
        "colleague": colleague,
        "sample_avatar": "jane_do.png"
    }

    create_sample_colleague(data)

    # instatiate Do Do:
    colleague = Colleagues(
        user_name = "dodo",
        email = "do.do@dodo.do",
        first_name = "Do",
        last_name = "Do",
        position = "dodo",
        confirmed = 1
    )
    colleague.set_password("aaa")
    data = {
        "company_id": registered_company.id,
        "colleague": colleague,
        "sample_avatar": "dodo.svg"
    }

    create_sample_colleague(data)

    # instatiate x more colleagues:
    x_more = 20

    usernames = open("fake_dataset/username.txt").readlines()
    emails = open("fake_dataset/fake_email.txt").readlines()
    first_names = open("fake_dataset/first_name.txt").readlines()
    last_names = open("fake_dataset/last_name.txt").readlines()
    positions = open("fake_dataset/position.txt").readlines()

    for x in range(x_more):

        colleague = Colleagues(
            user_name = get_random_item(usernames).strip(),
            email = get_random_item(emails),
            first_name = get_random_item(first_names),
            last_name = get_random_item(last_names).lower().title(),
            position = get_random_item(positions),
            confirmed = 1
        )
        colleague.set_password("aaa")
        data = {
            "company_id": registered_company.id,
            "colleague": colleague,
            "sample_avatar": None
        }

        create_sample_colleague(data)

    # create sample Idea Box:
    admin = Admins.query.filter(Admins.colleague_id == registered_colleague.id).first()
    for x in range(2):  
        new_box = Boxes(
            name = lorem.sentence().replace(".", ""),
            description = lorem.paragraph(),
            close_at = str_to_date(add_day(str_to_date(today()), x ).strftime('%Y-%m-%d')),
            admin_id = admin.id
        )

        try:
            print("Trying to add new Idea Box to the database...")
            db.session.add(new_box)
            db.session.commit()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            print("**************************************")
            print(error)
            print("New Idea Box not created!")
            print("new_box.name: ", new_box.name)
            print("new_box.description: ", new_box.description)
            print("new_box.close_at: ", new_box.close_at)
            print("new_box.admin_id: ", new_box.admin_id)
            db.session.rollback()

    # create sample Idea:
    colleagues = Colleagues.query.filter(Colleagues.company_id == registered_company.id).all()
    boxes = db.session.query(Boxes, Admins, Colleagues).filter(Boxes.admin_id == admin.id).all()
    for x in range(7):
        colleague = get_random_item(colleagues)
        sign = [
            "incognito",
            colleague.user_name,
            colleague.first_name,
            colleague.fullname()
        ]
        idea = Ideas(
            idea = lorem.paragraph(),
            sign = get_random_item(sign),
            box_id = get_random_item(boxes).Boxes.id,
            colleague_id = colleague.id
        )
        db.session.add(idea)

    try:
        db.session.commit()
    except:
        db.session.rollback()

    print("The sample company registered successfully!")

def create_sample_colleague(data):
    colleague = data["colleague"]
    company_id = data["company_id"]
    colleague.company_id = company_id
    sample_avatar = data["sample_avatar"]

    # insert new colleague to the colleague table:
    try:
        db.session.add(colleague)
        db.session.commit()
    except:
        db.session.rollback()

    # query the  id of the new created sample_colleague:
    colleague = Colleagues.query.filter_by(email = colleague.email).first()

    # copy the sample avatar:
    if sample_avatar:
        extension = get_extension(sample_avatar)
        location = f"static/sample_avatars/{sample_avatar}"
        destination = f"static/avatars/{colleague.id}.{extension}"
        shutil.copy2(location, destination)
        # upload to AWS:
        print(s3.upload(location, os.environ["S3_BUCKET"], f"avatars/{colleague.id}.{extension}"))
    
        # update database with the copied avatar:
        colleague.avatar = extension
        try:
            db.session.commit()
            print("Avatar copied")
        except:
            db.session.rollback()
            print("An error occured when copied avatar.")

def get_random_item(list):
    return random.choice(list)