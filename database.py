import psycopg2

conn = psycopg2.connect("dbname=postgres user=postgres password=amadeus")
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
def find_user(user_id):
    cur.execute("SELECT * FROM Users WHERE user_id = %s;", (user_id))
    return cur.fetchone()

#deleting user based on id
def delete_user(user_id):
    if (find_user(user_id)):
        cur.execute("DELETE FROM Users WHERE user_id = %s", (user_id))
        conn.commit()

#user1 is who the money is transferring from
#user2 is who the money goes to
def balance_transfer(user_id1, user_id2, amount):
    if confirm_user(user_id1) and confirm_user(user_id2) and confirm_balance(user_id1, amount):
        cur.execute("UPDATE Users SET balance = balance - %s WHERE user_id = %s", (amount, user_id1))
        cur.execute("UPDATE Users SET balance = balance + %s WHERE user_id = %s", (amount, user_id2))
        conn.commit()
        return True
    return False


def test_cases():
    val = find_user("6")
    print(val)
    delete_user("6")
    val = find_user("6")
    print(val)

cur.close()
conn.close()


