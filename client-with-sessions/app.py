from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Expense, bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-junior-dev-key'

api = Api(app)
migrate = Migrate(app, db)
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# --- AUTH RESOURCES ---
class Signup(Resource):
    def post(self):
        data = request.get_json()
        if User.query.filter_by(username=data.get('username')).first():
            return {"error": "Username taken"}, 422
        user = User(username=data['username'])
        user.password_hash = data['password']
        db.session.add(user)
        db.session.commit()
        return {"token": create_access_token(identity=user.id)}, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        if user and user.authenticate(data.get('password')):
            return {"token": create_access_token(identity=user.id)}, 200
        return {"error": "Invalid credentials"}, 401

# --- EXPENSE RESOURCES (CRUD + PAGINATION) ---
class ExpenseList(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        # 10 points for Pagination!
        pagination = Expense.query.filter_by(user_id=user_id).paginate(page=page, per_page=5)
        return [e.to_dict() for e in pagination.items], 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        new_exp = Expense(description=data['description'], amount=data['amount'], 
                          category=data.get('category'), user_id=user_id)
        db.session.add(new_exp)
        db.session.commit()
        return new_exp.to_dict(), 201

api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(ExpenseList, '/expenses')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
