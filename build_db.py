import database
import bcrypt

p1 = "password1"
p2 = "password2"
p3 = "password3"
p1 = bcrypt.hashpw(p1.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
p2 = bcrypt.hashpw(p2.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
p3 = bcrypt.hashpw(p3.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
database.make_user(("nicole", "Formato", "123 Abc", "Tallahassee", "FL", "32327", "User", "nicole", p1), 500, 800)
database.make_user(("jasmine", "Bob", "22 Street", "Tallahassee", "FL", "32327", "User", "jasmine", p2), 1500, 500)
database.make_user(("frankie", "Amanda", "23 Street", "Tallahassee", "FL", "32327", "User", "frankie", p3), 2000, 1000)

