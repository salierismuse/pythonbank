import psycopg2

conn = psycopg2.connect("dbname=postgres user=postgres password=amadeus")
cur = conn.cursor()

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

def transaction(transact_data):
    return 0


def test_cases():
    val = find_user("6")
    print(val)
    delete_user("6")
    val = find_user("6")
    print(val)

cur.close()
conn.close()


