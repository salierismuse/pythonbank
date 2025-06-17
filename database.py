import psycopg2

conn = psycopg2.connect("dbname=postgres user=postgres password=****")
cur = conn.cursor()

# cur.execute("SELECT * FROM testing;")
# cur.fetchone()


def make_user(first_name, last_name, balance, role):
    cur.execute("INSERT INTO Users (first_name, last_name, balance, role) VALUES (%s, %s, %s, %s)", (first_name, last_name, balance, role))
    conn.commit()

make_user("olivia", "fortnite", 2, "User")

cur.close()
conn.close()


