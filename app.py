from flask import Flask, request, render_template, session 
import database
import decimal
import bcrypt

app = Flask(__name__)

app.secret_key = "TESTING"

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        un = request.form["un"]
        pw = request.form["pw"]
        user_id = database.get_user_id(un)
        hashed_pw = database.get_password(user_id)
        if bcrypt.checkpw(pw.encode("utf-8"), hashed_pw.encode("utf-8")):              #check if password matches
           user_role = database.get_role(user_id)
           print(user_role)
           first_name = database.get_users_name(user_id) 
           checking_bal = database.get_bal(database.get_checking(user_id))
           saving_bal = database.get_bal(database.get_saving(user_id))
           session["user_id"] = user_id 

           return render_template("user_bank.html", name=first_name, check_bal=checking_bal[0], save_bal=saving_bal[0])
        else:
            return render_template("home.html", error="Invalid username or password")
        
    return render_template("home.html")

@app.route("/user_bank", methods=["GET", "POST"])
def users():
    user_id = session.get("user_id")
    if request.method == "POST":
        print("Form data:", request.form)
        type = request.form["type"]
        if type == "checkings":
            chain = database.get_transaction_chain(database.get_checking(user_id))
            session["account_id"] = database.get_checking(user_id)
            session["transactions"] = chain
            return render_template("user_account.html", transactions=chain)
        elif type == "savings":
            chain = database.get_transaction_chain(database.get_saving(user_id))
            session["account_id"] = database.get_saving(user_id)
            session["transactions"] = chain
            return render_template("user_account.html", transactions=chain)
    return render_template("user_bank.html")

@app.route("/user_account", methods=["GET", "POST"])
def user_account():
    account_id = session.get("account_id")
    if request.method == "POST":
        amount = decimal.Decimal((request.form["amount"]))
        account_to = request.form["to_id"]
        if database.balance_transfer(account_id, account_to, amount):
            chain = database.get_transaction_chain(account_id)
            return render_template("user_account.html", transactions=chain)
        else:
            chain = database.get_transaction_chain(account_id)
            return render_template("user_account.html", transactions=chain)
    chain = session.get("transactions")
    return render_template("user_account.html", transactions=chain)



    