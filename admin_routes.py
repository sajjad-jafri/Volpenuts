from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Admin, DryFruit, User, Offer, Order
from forms import LoginForm, DryFruitForm

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

@admin_bp.route("/")
def redirect_to_home():
    return redirect(url_for("admin_bp.home"))

@admin_bp.route("/home")
def home():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))
    offer = Offer.query.first()
    return render_template("admin_home.html", offer=offer)

@admin_bp.route("/dryfruits", methods=["GET", "POST"])
def dryfruits():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))
    form = DryFruitForm()
    if form.validate_on_submit():
        fruit = DryFruit(
            name=form.name.data,
            image=form.image.data,
            price=int(form.price.data),
            priority=form.priority.data
        )
        db.session.add(fruit)
        db.session.commit()
        return redirect(url_for("admin_bp.dryfruits"))
    fruits = DryFruit.query.order_by(DryFruit.priority.asc()).all()
    return render_template("admin_dryfruits.html", form=form, fruits=fruits)

@admin_bp.route("/users")
def users():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_bp.home"))
        else:
            flash("Invalid credentials")
    return render_template("admin_login.html", form=form)

@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_bp.login"))  # ✅ corrected

@admin_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))  # ✅ corrected

    fruit = DryFruit.query.get_or_404(id)
    form = DryFruitForm(obj=fruit)
    if form.validate_on_submit():
        fruit.name = form.name.data
        fruit.image = form.image.data
        fruit.price = int(form.price.data)
        fruit.priority = form.priority.data
        db.session.commit()
        return redirect(url_for("admin_bp.dryfruits"))  # ✅ corrected

    return render_template("edit.html", form=form)

@admin_bp.route("/delete/<int:id>")
def delete(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))  # ✅ corrected

    fruit = DryFruit.query.get_or_404(id)
    db.session.delete(fruit)
    db.session.commit()
    return redirect(url_for("admin_bp.dryfruits"))  # ✅ corrected

@admin_bp.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))  # ✅ corrected

    user = User.query.get_or_404(user_id)
    session.pop(f"cart_{user_id}", None)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "admin")
    return redirect(url_for("admin_bp.users"))  # ✅ corrected

@admin_bp.route("/offers")
def offers():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))
    offer = Offer.query.first()
    return render_template("admin_offers.html", offer=offer)

@admin_bp.route("/update_offer", methods=["POST"])
def update_offer():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_bp.login"))

    enabled = bool(request.form.get("enabled"))
    text = request.form.get("text", "").strip()
    discount = int(request.form.get("discount") or 0)
    min_order = int(request.form.get("min_order") or 0)

    offer = Offer.query.first()
    if not offer:
        offer = Offer()

    offer.enabled = enabled
    offer.text = text if enabled else ""
    offer.discount = discount if enabled else 0
    offer.min_order = min_order if enabled else 0

    db.session.add(offer)
    db.session.commit()
    flash("Offer updated successfully.", "admin")
    return redirect(url_for("admin_bp.offers"))


@admin_bp.route("/orders")
def orders():
    # Show all pending orders
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin_orders.html", orders=all_orders)

@admin_bp.route("/approve_order/<int:order_id>", methods=["POST"])
def approve_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = "Approved"
    db.session.commit()
    flash(f"Order {order.id} approved.", "success")
    return redirect(url_for("admin_bp.orders"))

@admin_bp.route("/cancel_order/<int:order_id>", methods=["POST"])
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = "Cancelled"
    db.session.commit()
    flash(f"Order {order.id} cancelled.", "danger")
    return redirect(url_for("admin_bp.orders"))

@admin_bp.route("/delete_order/<int:order_id>", methods=["POST"])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash(f"Order #{order.id} deleted.", "danger")
    return redirect(url_for("admin_bp.orders"))
