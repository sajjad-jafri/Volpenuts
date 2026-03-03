from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Order
from forms import UserSignupForm, UserLoginForm
from werkzeug.security import generate_password_hash
from flask_mail import Message

user_bp = Blueprint("user_bp", __name__)

# placeholders to be injected later
mail = None
serializer = None

@user_bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = UserSignupForm()
    if form.validate_on_submit():
        # Check for existing username or email
        existing_user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data) |
            (User.phone == form.phone.data)
        ).first()

        if existing_user:
            if existing_user.username == form.username.data:
                flash("Username already exists. Please choose another.", "warning")
            elif existing_user.email == form.email.data:
                flash("Email already registered. Please use a different one.", "warning")
            elif existing_user.phone == form.phone.data:
                flash("Phone number already in use. Please use a different one.", "warning")
            return redirect(url_for("user_bp.signup"))

        else:
            # ✅ Create new user only if no conflicts
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                address=form.address.data,
                phone=form.phone.data,
                password_hash=generate_password_hash(form.password.data)
            )
            db.session.add(new_user)
            db.session.commit()

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("user_bp.user_login"))

    return render_template("signup.html", form=form)

@user_bp.route("/user_login", methods=["GET", "POST"])
def user_login():
    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()
        if user and user.check_password(form.password.data):
            session["user_logged_in"] = True
            session["user_id"] = user.id
            session["username"] = user.username

            # ✅ Migrate guest cart to user cart
            guest_cart = session.get("cart", [])
            user_cart_key = f"cart_{user.id}"
            user_cart = session.get(user_cart_key, [])

            # ✅ Merge without duplicates
            for entry in guest_cart:
                if not any(
                    e["product_id"] == entry.get("product_id") and e["weight"] == entry.get("weight")
                    for e in user_cart
                ):
                    user_cart.append(entry)

            session[user_cart_key] = user_cart
            session.pop("cart", None)  # ✅ Clear guest cart

            return redirect(url_for("index"))
        else:
            flash("Invalid credentials")
    return render_template("user_login.html", form=form)


@user_bp.route("/user_logout")
def user_logout():
    session.pop("user_logged_in", None)
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop('_flashes', None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@user_bp.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not session.get("user_logged_in"):
        flash("Please log in first.", "warning")
        return redirect(url_for("user_bp.user_login"))

    # 🔑 Fetch newest orders first
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    for order in orders:
        order.total_price = sum(int(item["price"]) for item in order.items)
    return render_template("user_dashboard.html", orders=orders)

@user_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate reset token
            token = serializer.dumps(email, salt="password-reset-salt")
            reset_url = url_for("user_bp.reset_password", token=token, _external=True)

            # Send reset email
            msg = Message("Password Reset Request", recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_url}"
            mail.send(msg)

            flash("Password reset link has been sent to your email.", "success")
            return redirect(url_for("user_bp.user_login"))
        else:
            flash("No account found with that email.", "danger")
    return render_template("forgot_password.html")

@user_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)  # 1 hour expiry
    except Exception:
        flash("The reset link is invalid or expired.", "danger")
        return redirect(url_for("user_bp.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)  # assuming you have a set_password method
            db.session.commit()
            flash("Your password has been updated!", "success")
            return redirect(url_for("user_bp.user_login"))

    return render_template("reset_password.html")
