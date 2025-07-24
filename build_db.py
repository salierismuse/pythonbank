import database
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

p1 = hash_password("password1")
p2 = hash_password("password2")
p3 = hash_password("password3")
p4 = hash_password("password4")
p5 = hash_password("password5")

database.make_user(("nicole", "Formato", "123 Abc", "Tallahassee", "FL", "32327", "User", "nicole", p1), 500, 800)
database.make_user(("jasmine", "Bob", "22 Street", "Tallahassee", "FL", "32327", "User", "jasmine", p2), 1500, 500)
database.make_user(("frankie", "Amanda", "23 Street", "Tallahassee", "FL", "32327", "Empl", "frankie", p3), 2000, 1000)
database.make_user(("Landon", "Martin", "23 Street", "Tallahassee", "FL", "32327", "Admin", "landon", p4), 2000, 1000)
database.make_user(("Phil", "David", "23 Street", "Tallahassee", "FL", "32327", "Empl", "phil", p4), 2000, 1000)
