from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# ----------------- Models -----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------- Helper Function -----------------
def suggest_category(description):
    description = description.lower()

    food_keywords = ['food', 'restaurant', 'pizza', 'burger', 'zomato', 'swiggy']
    transport_keywords = ['uber', 'ola', 'taxi', 'bus', 'train', 'cab']
    housing_keywords = ['rent', 'apartment', 'flat']
    utility_keywords = ['electricity', 'bill', 'water', 'gas', 'internet']
    shopping_keywords = ['amazon', 'flipkart', 'shopping', 'clothes']

    if any(word in description for word in food_keywords):
        return "Food"
    elif any(word in description for word in transport_keywords):
        return "Transport"
    elif any(word in description for word in housing_keywords):
        return "Housing"
    elif any(word in description for word in utility_keywords):
        return "Utilities"
    elif any(word in description for word in shopping_keywords):
        return "Shopping"
    else:
        return "Other"

# ----------------- Routes -----------------
@app.route('/')
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    category_data = {}

    for txn in transactions:
        category_data[txn.category] = category_data.get(txn.category, 0) + txn.amount

    return render_template('index.html', transactions=transactions, category_data=category_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    amount = float(request.form['amount'])
    description = request.form['description']
    category = suggest_category(description)

    new_txn = Transaction(amount=amount, description=description, category=category, user_id=current_user.id)
    db.session.add(new_txn)
    db.session.commit()
    flash("Transaction added!", "success")
    return redirect(url_for('index'))

@app.route('/upload_csv', methods=['POST'])
@login_required
def upload_csv():
    flash("CSV upload feature coming soon!", "info")
    return redirect(url_for('index'))

# ----------------- Start -----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)