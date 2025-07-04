from flask import Flask, request, render_template 
import database


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        un = request.form.get("un")
        pw = request.form.get("pw")
        if database.find_user(un):
           user_id = database.get_user_id(un)
           first_name = database.get_users_name(user_id) 
           return render_template("user_bank.html", name=first_name)
        return render_template("home.html")
    return render_template("home.html")

@app.route("/user_bank")
def users():
    return render_template("user_bank.html")