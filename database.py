import psycopg2

conn = psycopg2.connect("dbname=testing user=postgres password=amadeus")
cur = conn.cursor()

#to determine if the user exists or not
def confirm_user(user_id):
    cur.execute("SELECT * FROM Users WHERE user_id = %s;", (user_id,))
    if (cur.fetchone() == None):
        return False
    return True
    
#confirming if an amount can be subtracted
#possibly add way for overdrafts later
def confirm_balance(user_id, amount):
    if not confirm_user(user_id):
        return False
    cur.execute("SELECT Balance FROM Users WHERE user_id = %s;", (user_id))
    val = cur.fetchone()
    if (val[0] - amount) >= 0:
        return True
    return False

# create user!
def make_user(user_data):
    cur.execute("INSERT INTO Users (first_name, last_name, balance, role) VALUES (%s, %s, %s, %s)", (user_data[0], user_data[1], user_data[2], user_data[3]))
    conn.commit()

#user look-up based on id
def find_user(user_name):
    cur.execute("SELECT * FROM Users WHERE username = %s;", (user_name,))
    return cur.fetchone()

#return user_id based on un
#note, make usernames unique
def get_user_id(user_name):
    cur.execute("SELECT user_id FROM Users WHERE username = %s;", (user_name,))
    return cur.fetchone()

def get_users_name(user_id):
    cur.execute("SELECT first_name FROM Users WHERE user_id = %s;", (user_id,))
    return cur.fetchone()

#deleting user based on id
def delete_user(user_id):
    if (find_user(user_id)):
        cur.execute("DELETE FROM Users WHERE user_id = %s", (user_id))
        conn.commit()

#user1 is who the money is transferring from
#user2 is who the money goes to
def balance_transfer(user_id1, user_id2, amount):
    if withdrawal(user_id1, amount) and deposit(user_id2, amount):
        cur.execute("INSERT INTO Transactions (from_user_id, to_user_id, amount) VALUES (%s, %s, %s)", (user_id1, user_id2, amount))
        conn.commit()
        return True
    return False

#basic one user withdrawal
#note, no commit
def withdrawal(user_id, amount):
    if confirm_user(user_id) and confirm_balance(user_id, amount):
        cur.execute("UPDATE Users SET balance = balance - %s WHERE user_id = %s", (amount, user_id))
        return True
    return False

#a singular withdrawal that commits
def withdrawal_single(user_id, amount):
    if withdrawal(user_id, amount):
        conn.commit()
        return True
    return False

#basic one user deposit
#note, no commit
def deposit(user_id, amount):
    if confirm_user(user_id):
        cur.execute("UPDATE Users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
        return True
    return False

#a singular deposit that commits
def deposit_single(user_id, amount):
    if deposit(user_id, amount):
        conn.commit()
        return True
    return False

def test_cases():
    val = find_user("6")
    print(val)
    delete_user("6")
    val = find_user("6")
    print(val)
