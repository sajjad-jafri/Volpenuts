from models import db, Admin
from flask import session

def seed_admin():
    if Admin.query.count() == 0:
        admin = Admin(username="admin")
        admin.set_password("brunuts123")  # Change this password
        db.session.add(admin)
        db.session.commit()

def inject_cart_count():
    user_id = session.get("user_id")
    cart_key = f"cart_{user_id}" if user_id else "cart"
    cart = session.get(cart_key, [])
    return dict(cart_count=len(cart))