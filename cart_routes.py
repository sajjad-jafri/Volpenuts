from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, DryFruit, Offer, Order, User
import json
import qrcode
import io
import base64

cart_bp = Blueprint("cart_bp", __name__)

@cart_bp.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    weight = request.form.get("weight", "200gm")
    fruit = DryFruit.query.get_or_404(product_id)

    # Calculate price
    if weight == "200gm":
        price = int(fruit.price * 0.4)
    else:
        price = fruit.price

    user_id = session.get("user_id")
    cart_key = f"cart_{user_id}" if user_id else "cart"
    cart = session.get(cart_key, [])

    # ✅ Check if item already exists
    already_in_cart = any(entry["product_id"] == product_id and entry["weight"] == weight for entry in cart)
    if already_in_cart:
        flash(f"{fruit.name} ({weight}) is already in your cart.", "warning")
    else:
        cart.append({
            "product_id": fruit.id,
            "item": fruit.name,
            "weight": weight,
            "price": price
        })
        session[cart_key] = cart
        flash(f"{fruit.name} added to cart.", "success")

    return redirect(url_for("index"))

@cart_bp.route("/checkout", methods=["POST"])
def checkout():
    if not session.get("user_logged_in"):
        flash("Please log in to continue.", "warning")
        return redirect(url_for("user_bp.user_login"))

    user_id = session.get("user_id")
    user = User.query.get_or_404(user_id)

    use_different_address = "different_address" in request.form
    use_different_phone = "different_phone" in request.form

    address = request.form.get("address") if use_different_address else user.address
    phone = request.form.get("phone") if use_different_phone else user.phone

    if not address or not phone:
        flash("Address and phone number are required.", "danger")
        return redirect(url_for("cart_bp.cart"))

    session["checkout_address"] = address
    session["checkout_phone"] = phone

    return redirect(url_for("cart_bp.place_order"))

@cart_bp.route("/cart")
def cart():
    user_id = session.get("user_id")
    cart_key = f"cart_{user_id}" if user_id else "cart"
    cart = session.get(cart_key, [])

    total = sum(item["price"] for item in cart)
    offer = Offer.query.first()

    discount = 0
    discount_amount = 0

    if offer and offer.enabled and offer.discount and total >= offer.min_order:
        discount = offer.discount
        discount_amount = int(total * discount / 100)
        total -= discount_amount

    # ✅ Fetch user if logged in
    user = None
    if user_id:
        user = User.query.get(user_id)
    return render_template("cart.html", cart=cart, total=total,
                           discount=discount, discount_amount=discount_amount,
                           min_order=offer.min_order if offer else 0, user=user)


@cart_bp.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    product_id = int(request.form["product_id"])
    weight = request.form["weight"]

    user_id = session.get("user_id")
    cart_key = f"cart_{user_id}" if user_id else "cart"

    cart = session.get(cart_key, [])
    updated_cart = [
        entry for entry in cart
        if not (entry.get("product_id") == product_id and entry.get("weight") == weight)
    ]
    session[cart_key] = updated_cart

    # Optional: get product name for flash message
    fruit = DryFruit.query.get(product_id)
    item_name = fruit.name if fruit else "Item"

    flash(f"{item_name} ({weight}) removed from cart.", "warning")
    return redirect(url_for("cart_bp.cart"))

@cart_bp.route("/place_order")
def place_order():
    if not session.get("user_logged_in"):
        flash("Please log in to place your order.", "warning")
        return redirect(url_for("user_bp.user_login"))

    # Proceed with order placement logic
    # e.g., save order to DB, clear cart, show confirmation
    '''
    session["cart"] = []
    flash("Order placed successfully!", "success")
    return redirect(url_for("dashboard"))
    '''
    ##########from here###############
    user_id = session.get("user_id")
    cart_key = f"cart_{user_id}" if user_id else "cart"
    cart = session.get(cart_key, [])
    total = sum(item["price"] for item in cart)

    upi_id = "mohdsajjad261@ybl"
    payee_name = "VolpeNuts"
    payment_url = f"upi://pay?pa={upi_id}&pn={payee_name}&am={total}&cu=INR"

    qr = qrcode.make(payment_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()
    ##########till here###############

    return render_template("place_order.html", qr_code=qr_b64, total=total)

@cart_bp.route("/confirm_order", methods=["POST"])
def confirm_order():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to confirm your order.", "warning")
        return redirect(url_for("user_bp.user_login"))

    cart_key = f"cart_{user_id}"
    cart = session.get(cart_key, [])

    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart_bp.cart"))

    # Fetch user details (example: from User model)
    user = User.query.get(user_id)


    # ✅ Pull overridden values from session
    address = session.get("checkout_address", user.address)
    phone = session.get("checkout_phone", user.phone)

    # ✅ Create new order with status 'Pending'
    new_order = Order(
        user_id=user.id,
        user_name=user.username,
        user_address=address,       # will fetch either signup address or manual address
        phone_number=phone,         # will fetch signup phone by default but manual if user select change
        items=cart,  # you may serialize this into JSON
        status="Pending"
    )
    db.session.add(new_order)
    db.session.commit()

    # ✅ Clear cart
    session[cart_key] = []

    flash("Order confirmed! Status: Pending approval.", "success")
    return redirect(url_for("user_bp.dashboard"))