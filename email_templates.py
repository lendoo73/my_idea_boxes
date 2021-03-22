from flask import render_template

def confirm_email_txt(first_name, code):
    return f"""
Hi {first_name},

This is a confirmation email before your first login to the Idea Box.

Please enter the following 6 digit to the confirmation field:
    
{code}

and click on 'Confirm my Email button'.

Kind Regards,

Idea Box
"""

def confirm_email_HTML(first_name, code):
    print(session["url"])
    return render_template(
        "email_confirmation_template.html",
        first_name = first_name,
        code = code
    )