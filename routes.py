'''
this route is for contact us page
Thank you email will be sent to user
'''

from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_mail import Message

contact_bp = Blueprint("contact_bp", __name__)

# We'll inject mail later
mail = None

@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message_text = request.form.get("message")

        # ✅ Send enquiry to care@volpenuts.com
        enquiry_msg = Message(
            subject=f"New Enquiry from {name}",
            recipients=["care@volpenuts.com"]
        )
        enquiry_msg.body = f"""
        Name: {name}
        Email: {email}
        Phone: {phone}
        Message:
        {message_text}
        """

        # ✅ Send thank-you email to user
        thankyou_msg = Message(
            subject="Thanks for contacting VolpeNuts!",
            recipients=[email]
        )
        thankyou_msg.body = f"""
Dear {name},

Thank you for reaching out to VolpeNuts. We’ve received your message and will get back to you shortly.

Best regards,
Team VolpeNuts
        """
        mail.send(thankyou_msg)
        try:
            mail.send(enquiry_msg)
            mail.send(thankyou_msg)
            flash("Your enquiry has been sent successfully! Please check your email for confirmation.", "success")
        except Exception as e:
            print("Mail send failed:", e)
            flash(f"Error sending mail: {e}", "danger")


        return redirect(url_for("contact"))

    return render_template("contact.html")
