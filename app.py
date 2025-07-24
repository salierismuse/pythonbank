from flask import Flask, request, render_template, session, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from functools import wraps
import database
import decimal
import bcrypt


app = Flask(__name__)

app.secret_key = "TESTING"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)
def required_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def required_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] not in roles:
                return redirect('/')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def home():
    if request.method == "POST":
        un = request.form["un"]
        pw = request.form["pw"]
        user_id_check = database.get_user_id(un)
        if not user_id_check:
            return render_template("home.html", error="Invalid username or password")
        user_id = user_id_check[0]
        hashed_pw = database.get_password(user_id)
        if bcrypt.checkpw(pw.encode("utf-8"), hashed_pw.encode("utf-8")):              #check if password matches
           user_role = database.get_role(user_id)
           first_name = database.get_users_name(user_id) 
           checking_bal = database.get_bal(database.get_checking(user_id))
           saving_bal = database.get_bal(database.get_saving(user_id))
           session["user_id"] = user_id 
           session["name"] = first_name
           session["check_bal"] = checking_bal[0]
           session["saving_bal"] = saving_bal[0]
           session["user_role"] = user_role

           if user_role == "Admin":
               return redirect("admin_home")
           elif user_role == "Empl":
                return redirect("/employee_home")
           elif user_role == "User": 
                return redirect("/user_bank")
           else:
                return render_template("home.html", error="Invalid username or password")
        else:
            return render_template("home.html", error="Invalid username or password")

    return render_template("home.html")

@app.route("/user_bank", methods=["GET", "POST"])
@required_login
def users():
    user_id = session.get("user_id")
    if not user_id:
        return render_template("home.html", error="Log in to view account details")
    name = session.get("name")
    check_bal = session.get("check_bal")
    saving_bal = session.get("saving_bal")
    if request.method == "POST":
        print("Form data:", request.form)
        type = request.form["type"]
        if type == "checkings":
            chain = database.get_transaction_chain(database.get_checking(user_id))
            session["account_id"] = database.get_checking(user_id)
            session["transactions"] = chain
            return redirect("/user_account")
        elif type == "savings":
            chain = database.get_transaction_chain(database.get_saving(user_id))
            session["account_id"] = database.get_saving(user_id)
            session["transactions"] = chain
            return redirect("/user_account")
    return render_template("user_bank.html", user_id=user_id, name=name, check_bal=check_bal, saving_bal=saving_bal)

@app.route("/user_account", methods=["GET", "POST"])
@limiter.limit("30 per minute")
@required_login
def user_account():
    account_id = session.get("account_id")
    chain = session["transactions"]
    if not account_id:
        return render_template("home.html", error="Log in to view account details")
    if request.method == "POST":
        amount = decimal.Decimal((request.form["amount"]))
        account_to = request.form["to_id"]
        print(amount)
        if database.balance_transfer(account_id, account_to, amount):
            chain = database.get_transaction_chain(account_id)
            checking_bal = database.get_bal(database.get_checking(session.get("user_id")))
            saving_bal = database.get_bal(database.get_saving(session.get("user_id")))
            session["check_bal"] = checking_bal[0]
            session["saving_bal"] = saving_bal[0]
            return render_template("user_account.html", transactions=chain, account_id = account_id)
        else:
            chain = database.get_transaction_chain(account_id)
            return render_template("user_account.html", transactions=chain, account_id = account_id)
    chain = session.get("transactions")
    return render_template("user_account.html", transactions=chain, account_id = account_id)


@app.route("/create_account", methods=["GET", "POST"])
@required_login
@required_role('Empl', 'Admin')
def create_account():
    user_id = session.get("user_id")
    user_role = session.get("user_role")
    if request.method == "POST":
        username = request.form["username"]
        if database.get_user_id(username):
            return render_template("create_account.html", error="Username already exists. Please choose another.")
        first = request.form["first name"]
        last = request.form["last name"]
        street = request.form["street"]
        city = request.form["city"]
        state = request.form["state"]
        zip_code = request.form["zip"]
        password = request.form["password"]
        checkings = request.form["checking"]
        saving = request.form["saving"]
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        account_info = (first, last, street, city, state, zip_code, "User", username, hashed_pw)
        if database.make_user(account_info, checkings, saving):
            if user_role == "Admin":
                return redirect("/admin_home")
            elif user_role == "Empl":
                return redirect("/employee_home")
            else:
                return redirect("/")
        else:
            return render_template("create_account.html", error="Account creation failed.")
    return render_template("create_account.html")



@app.route("/employee_home", methods=["GET", "POST"])
@required_login
@required_role('Empl', 'Admin')
def employee_home():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/")
    user_role = database.get_role(user_id)
    if user_role != "Empl":
        session.clear()
        return redirect("/")
    users = database.get_all_users_and_accounts() 
    if request.method == "POST":
        user_id_to_delete = request.form.get("user_id_to_delete")
        if user_id_to_delete != None:
            database.delete_user(int(user_id_to_delete))
            users = database.get_all_users_and_accounts()
            return render_template("employee_home.html", users=users)
    return render_template("employee_home.html", users=users)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)

@app.route("/process_pending", methods=["POST"])
@required_login
@required_role('Admin')
def process_pending():
    # SECURITY: Restrict this route to admin users only!
    # Example: if session.get("user_id") != <admin_id>: return "Access denied", 403

    from database import process_all_pending
    result = process_all_pending()
    return result

@app.route("/admin_home", methods=["GET", "POST"])
@required_login
@required_role('Admin')
def admin_home():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/")
    user_role = database.get_role(user_id)
    if user_role != "Admin":
        session.clear()
        return redirect("/")
    users = database.get_all_users_and_accounts()
    employees = database.get_all_employees()
    if request.method == "POST":
        user_id_to_delete = request.form.get("user_id_to_delete")
        if user_id_to_delete != None:
            database.delete_user(int(user_id_to_delete))
            users = database.get_all_users_and_accounts()
            employees = database.get_all_employees()
            return render_template("admin_home.html", users = users, employees = employees)
    return render_template("admin_home.html", users=users, employees=employees)



if __name__ == "__main__":
    app.run(debug=True)
