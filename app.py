from flask import Flask, request, render_template, session, redirect 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
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

@app.route("/", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def home():
    if request.method == "POST":
        un = request.form["un"]
        pw = request.form["pw"]
        user_id = database.get_user_id(un)
        user_id = user_id
        if not user_id:
            return render_template("home.html", error="Invalid username or password")
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


           return redirect("/user_bank")
        else:
            return render_template("home.html", error="Invalid username or password")

    return render_template("home.html")

@app.route("/user_bank", methods=["GET", "POST"])
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
@limiter.limit("5 per minute")
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
            return render_template("user_account.html", transactions=chain)
        else:
            chain = database.get_transaction_chain(account_id)
            return render_template("user_account.html", transactions=chain)
    chain = session.get("transactions")
    return render_template("user_account.html", transactions=chain)


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    user_id = session.get("user_id")
    if request.method == "POST":
        first = request.form["first name"]
        last = request.form["last name"]
        street = request.form["street"]
        city = request.form["city"]
        state = request.form["state"]
        zip = request.form["zip"]
        username = request.form["username"]
        password = request.form["password"]
        checkings = request.form["checking"]
        saving = request.form["saving"]
        account_info = (first, last, street, city, state, zip, "User", username, password)
        if database.make_user(account_info, checkings, saving):
            return redirect("/")
    if database.get_role(user_id) == "Empl":
        return render_template("create_account.html")
    else:
        return render_template("create_account.html")
    
    if __name__ == "__main__":
        app.run(debug=True)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)

@app.route("/process_pending", methods=["POST"])
def process_pending():
    # SECURITY: Restrict this route to admin users only!
    # Example: if session.get("user_id") != <admin_id>: return "Access denied", 403

    from database import process_all_pending
    result = process_all_pending()
    return result