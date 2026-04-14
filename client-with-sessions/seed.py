from app import app
from models import db, User, Expense

with app.app_context():
    User.query.delete()
    Expense.query.delete()
    u = User(username="test_user")
    u.password_hash = "1234"
    db.session.add(u)
    db.session.commit()
    print("Database Seeded!")