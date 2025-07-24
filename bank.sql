CREATE TABLE Users (
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


Create Table Accounts (
	account_id SERIAL PRIMARY KEY,
	user_id INT REFERENCES Users(user_id) ON DELETE SET NULL,
	balance DECIMAL(10, 2) DEFAULT 0.00,
	interest DECIMAL(4, 2) DEFAULT 0.04,
	role VARCHAR(10) CHECK(role IN ('Checkings', 'Savings'))
);

CREATE TABLE Transactions (
	transaction_id SERIAL PRIMARY KEY,
	from_account_id int REFERENCES Accounts(account_id),
	to_account_id INT REFERENCES Accounts(account_id),
	amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
	date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE PendingTransactions (
    id SERIAL PRIMARY KEY,
    from_account_id INT,
    to_account_id INT,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Add any extra columns as needed
    status TEXT DEFAULT 'pending'
);


