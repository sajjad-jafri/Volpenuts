from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, DryFruit, Offer
from utils import seed_admin, inject_cart_count
from admin_routes import admin_bp
from user_routes import user_bp
from cart_routes import cart_bp
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///volpenuts.db'
app.config['SECRET_KEY'] = '9f3c2a1e8b7d4c6f9a2b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4g'
db.init_app(app)

app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(cart_bp)

@app.context_processor
def inject_cart():
    return inject_cart_count()

@app.template_filter('loads')
def loads_filter(s):
    return json.loads(s)

@app.route("/", methods=["GET", "POST"])
def index():
    dry_fruits = DryFruit.query.order_by(DryFruit.priority.asc()).all()

    # ✅ Use user-specific cart key
    user_id = session.get("user_id")
    cart_key = f"cart_{user_id}" if user_id else "cart"
    cart = session.get(cart_key, [])

    if request.method == "POST":
        item = request.form["item"]
        weight = request.form["weight"]
        price = int(request.form["base_price"])
        if weight == "200gm":
            price = (price // 5) * 2

        # ✅ Get product_id from form or match by name
        fruit = next((f for f in dry_fruits if f.name == item), None)
        if fruit:
            product_id = fruit.id

            # ✅ Check if item already exists
            already_in_cart = any(entry["product_id"] == product_id and entry["weight"] == weight for entry in cart)
            if already_in_cart:
                flash(f"{item} ({weight}) is already in your cart.", "warning")
            else:
                cart.append({
                    "product_id": product_id,
                    "item": item,
                    "weight": weight,
                    "price": price
                })
                session[cart_key] = cart
                flash(f"{item} added to cart.", "success")
        else:
            flash("Product not found.", "warning")

    # ✅ Build cart_items list using product_id
    cart_items = [entry["product_id"] for entry in cart if "product_id" in entry]
    cart_count = len(cart)
    offer = Offer.query.first()
    return render_template("index.html", dry_fruits=dry_fruits, cart_items=cart_items, cart_count=cart_count,
                           offer=offer)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Handle form submission here
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form.get("phone")
        message = request.form["message"]
        # Save to DB or send email
        flash("Thank you for reaching out!", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")


# -------------------- Run --------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True)
