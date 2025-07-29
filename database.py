import psycopg2
import datetime
import bcrypt 
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

conn = psycopg2.connect("dbname=postgres user=postgres password=postgres")
cur = conn.cursor()

try:
    cur.execute("SELECT * FROM Users;")
except: 
    conn.rollback()
    cur.execute("""CREATE TABLE Users (
        user_id SERIAL PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        street TEXT,
        city TEXT,
        st TEXT,
        zip_code TEXT,
        date_created DATE DEFAULT CURRENT_DATE,
        role VARCHAR(10) CHECK(role IN('Empl', 'User', 'Admin')),
        username VARCHAR(30) UNIQUE NOT NULL,
        pw VARCHAR(72) NOT NULL

    );
    """)
    cur.execute("""Create Table Accounts (
        account_id SERIAL PRIMARY KEY,
        user_id INT REFERENCES Users(user_id) ON DELETE SET NULL,
        balance DECIMAL(10, 2) DEFAULT 0.00,
        interest DECIMAL(4, 2) DEFAULT 0.04,
        role VARCHAR(10) CHECK(role IN ('Checkings', 'Savings'))
    );
    """)

    cur.execute("""CREATE TABLE Transactions (
        transaction_id SERIAL PRIMARY KEY,
        from_account_id int REFERENCES Accounts(account_id),
        to_account_id INT REFERENCES Accounts(account_id),
        amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
        date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    );
    """)

    cur.execute("""CREATE TABLE PendingTransactions (
        id SERIAL PRIMARY KEY,
        from_account_id INT,
        to_account_id INT,
        amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
        date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        status TEXT DEFAULT 'pending'
    );
    """)
    conn.commit()

DB_CONN_STR = "dbname=postgres user=postgres password=postgres"

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
    try:
        cur.execute(
            "INSERT INTO Users (first_name, last_name, street, city, st, zip_code, role, username, pw) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5], user_data[6], user_data[7], user_data[8])
        )
        cur.execute("SELECT user_id FROM Users WHERE username = %s", (user_data[7],))
        id = cur.fetchone()[0]
        Checkings = (id, checking_data, "Checkings")
        Savings = (id, saving_data, "Savings")
        make_account(Checkings)
        make_account(Savings)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False


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
    cur.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
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
def _get_db():
    """Helper to open a fresh connection & cursor."""
    conn = psycopg2.connect(DB_CONN_STR)
    cur  = conn.cursor()
    return conn, cur

def process_transaction(pending_txn):
    """
    Worker function: each process opens its own DB connection.
    pending_txn = (from_acct, to_acct, amount, date_sent, txn_id)
    """
    acct1, acct2, amount, date_sent, txn_id = pending_txn
    conn, cur = _get_db()
    try:
        # withdraw
        cur.execute(
            "UPDATE Accounts SET balance = balance - %s WHERE account_id = %s",
            (amount, acct1)
        )
        # deposit
        cur.execute(
            "UPDATE Accounts SET balance = balance + %s WHERE account_id = %s",
            (amount, acct2)
        )
        # record transaction
        cur.execute(
            "INSERT INTO Transactions (from_account_id, to_account_id, amount, date_sent) VALUES (%s, %s, %s, %s)",
            (acct1, acct2, amount, date_sent)
        )
        # delete pending
        cur.execute(
            "DELETE FROM PendingTransactions WHERE id = %s",
            (txn_id,)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[worker] failed txn {txn_id}: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def process_all_pending(pool_size=None):
    """
    Fetch all pending transactions, then map them across a pool.
    """
    conn, cur = _get_db()
    cur.execute("SELECT from_account_id, to_account_id, amount, date_sent, id FROM PendingTransactions")
    pending = cur.fetchall()
    cur.close()
    conn.close()

    if not pending:
        return "✔ No pending transactions."

    # spawn a pool (defaults to os.cpu_count())
    with Pool(processes=pool_size) as pool:
        results = pool.map(process_transaction, pending)

    succeeded = sum(1 for r in results if r)
    failed    = len(results) - succeeded
    return f"Processed {succeeded}/{len(results)} transactions." + (f" ({failed} failed)" if failed else "")

#applying interest to single account
def apply_interest(account_data):
    #each thread has its own db
    acc_id, balance, interest_rate = account_data
    thread_conn, thread_cur = _get_db()

    try:
        monthly_interest = float(balance) * (float(interest_rate) / 12)     #monthy interest calc
        new_balance = float(balance) + monthly_interest

        thread_cur.execute(
            "UPDATE Accounts SET balance = %s WHERE account_id = %s",       #updating account balance 
            (new_balance, acc_id)
        )
        thread_cur.execute(
            "INSERT INTO Transactions (from_account_id, to_account_id, amount, date_sent) VALUES (%s, %s, %s, %s)",      #updating account transaction
            (acc_id, acc_id, monthly_interest, datetime.datetime.now())
        )
        thread_conn.commit()
        return True
    
    except Exception as e:
        thread_conn.rollback()
        print(f"Interest calculation failed for account {acc_id}: {e}")
        return False
    
    finally:
        thread_cur.close()
        thread_conn.close()

#for monthly interest of all saving accounts
def calc_all_interest():
    cur.execute("SELECT account_id, balance, interest FROM Accounts WHERE role='Savings'")
    saving_accounts = cur.fetchall()
    
    if not saving_accounts:
        return "No saving accounts found",[]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(apply_interest, saving_accounts)

    return f"Interest applied to {len(saving_accounts)} accounts.", []


def get_all_users_and_accounts():
    cur.execute("""
        SELECT u.user_id, u.first_name, u.last_name, u.username, u.role,
               a.account_id, a.balance, a.role as account_type, a.interest
        FROM Users u
        JOIN Accounts a ON u.user_id = a.user_id
        WHERE u.role = 'User'
        ORDER BY u.user_id, a.account_id
    """)
    return cur.fetchall()


def get_all_employees():
    cur.execute("""
        SELECT user_id, first_name, last_name, username, role
        FROM Users
        WHERE role = 'Empl'
        ORDER BY user_id
    """)
    return cur.fetchall()

