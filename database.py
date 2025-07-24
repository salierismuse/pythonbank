import psycopg2
import datetime
import bcrypt 
from multiprocessing import Pool

conn = psycopg2.connect("dbname=testing user=postgres password=amadeus")
cur = conn.cursor()

#get pw
def get_password(user_id):
    if confirm_user(user_id):
        cur.execute("SELECT pw FROM Users WHERE user_id = %s;", (user_id,))
        val = cur.fetchone()
        return val[0]
    return None

#to determine if the user exists or not
def confirm_user(user_id):
    cur.execute("SELECT * FROM Users WHERE user_id = %s;", (user_id,))
    if (cur.fetchone() == None):
        return False
    return True

def confirm_account(account_id):
    cur.execute("SELECT * FROM Accounts WHERE account_id = %s;", (account_id,))
    if (cur.fetchone() == None):
        return False
    return True
    
#fetching transaction chain
def get_transaction_chain(account_id):
    cur.execute("SELECT amount, from_account_id, to_account_id, date_sent FROM Transactions WHERE from_account_id = %s OR to_account_id = %s;", (account_id, account_id,))
    vals = cur.fetchall()
    return vals

def find_account(account_id):
    cur.execute("SELECT * FROM Transactions WHERE account_id = %s;", (account_id,))
    
    if (cur.fetchone() == None):
        return False
    return True

def get_checking(user_id):
    cur.execute("SELECT account_id FROM Accounts WHERE user_id = %s AND role = 'Checkings'", (user_id,))
    acc = cur.fetchone()
    return acc[0]

def get_saving(user_id):
    cur.execute("SELECT account_id FROM Accounts WHERE user_id = %s AND role = 'Savings'", (user_id,))
    acc = cur.fetchone()
    return acc[0]

def get_role(user_id):
    if confirm_user(user_id):
        cur.execute("SELECT role FROM Users WHERE user_id = %s", (user_id,))
        role = cur.fetchone()
        return role[0]
    else:
        return None        

#confirming if an amount can be subtracted
#possibly add way for overdrafts later
def confirm_balance(account_id, amount):
    if not confirm_account(account_id):
        return False
    cur.execute("SELECT Balance FROM Accounts WHERE account_id = %s;", (account_id,))
    val = cur.fetchone()
    if (float(val[0]) - float(amount)) >= 0:
        return True
    return False



# create user!
def make_user(user_data, checking_data, saving_data):
    hashed_pw = bcrypt.hashpw(user_data[8].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cur.execute(
        "INSERT INTO Users (first_name, last_name, street, city, st, zip_code, role, username, pw) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5], user_data[6], user_data[7], hashed_pw)
    )
    cur.execute("SELECT user_id FROM Users WHERE username = %s", (user_data[7],))
    id = cur.fetchone()[0]
    Checkings = (id, checking_data, "Checkings")
    Savings = (id, saving_data, "Savings")
    make_account(Checkings)
    make_account(Savings)
    conn.commit()

def make_account(account_data):
    cur.execute("INSERT INTO Accounts (user_id, balance, role) VALUES (%s, %s, %s)", (account_data))

#user look-up based on id
def find_user(user_name):
    cur.execute("SELECT * FROM Users WHERE username = %s;", (user_name,))
    return cur.fetchone()

#return user_id based on un
#note, make usernames unique
def get_user_id(user_name):
    cur.execute("SELECT user_id FROM Users WHERE username = %s;", (user_name,))
    return (cur.fetchone())

def get_bal(account_id):
    cur.execute("SELECT balance FROM Accounts WHERE account_id = %s", (account_id,))
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
# needs to be rewritten to deal with accounts now.
def balance_transfer(account_id1, account_id2, amount):
    if withdrawal(account_id1, amount) and deposit(account_id2, amount):
        cur.execute("INSERT INTO Transactions (from_account_id, to_account_id, amount, date_sent) VALUES (%s, %s, %s, %s)", (account_id1, account_id2, float(amount), datetime.datetime.now()))
        conn.commit()
        return True
    return False

#basic one user withdrawal
#note, no commit
def withdrawal(account_id, amount):
    if confirm_account(account_id) and confirm_balance(account_id, amount):
        cur.execute("UPDATE Accounts SET balance = balance - %s WHERE account_id = %s", (float(amount), account_id))
        return True
    return False

#a singular withdrawal that commits
def withdrawal_single(account_id, amount):
    if withdrawal(account_id, amount):
        conn.commit()
        return True
    return False

#basic one user deposit
#note, no commit
def deposit(account_id, amount):
    if confirm_account(account_id):
        cur.execute("UPDATE Accounts SET balance = balance + %s WHERE account_id = %s", (float(amount), account_id))
        return True
    return False

#a singular deposit that commits
def deposit_single(account_id, amount):
    if deposit(account_id, amount):
        conn.commit()
        return True
    return False

def test_cases():
    val = find_user("6")
    print(val)
    delete_user("6")
    val = find_user("6")
    print(val)

#This is to help with Parallization 
def process_transaction(pending_txn):
    account_id1, account_id2, amount, date_sent, txn_id = pending_txn
    # Try to perform withdrawal/deposit
    if withdrawal(account_id1, amount) and deposit(account_id2, amount):
        cur.execute(
            "INSERT INTO Transactions (from_account_id, to_account_id, amount, date_sent) VALUES (%s, %s, %s, %s)",
            (account_id1, account_id2, amount, date_sent)
        )
        cur.execute("DELETE FROM PendingTransactions WHERE id = %s", (txn_id,))
        conn.commit()
        return True
    return False

def process_all_pending():
    cur.execute("SELECT from_account_id, to_account_id, amount, date_sent, id FROM PendingTransactions")
    pending_txns = cur.fetchall()
    if not pending_txns:
        return "No pending transactions to process."
    with Pool() as pool:
        results = [pool.apply_async(process_transaction, (txn,)) for txn in pending_txns]
        [r.get() for r in results]  # Wait for all to finish
    return f"Processed {len(pending_txns)} transactions."

def get_all_users_and_accounts():
    cur.execute("""
        SELECT u.user_id, u.first_name, u.last_name, u.username, u.role,
               a.account_id, a.balance, a.role as account_type, a.interest
        FROM Users u
        JOIN Accounts a ON u.user_id = a.user_id
        ORDER BY u.user_id, a.account_id
    """)
    return cur.fetchall()

