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
	username VARCHAR(30),
	pw VARCHAR(72)
);


Create Table Accounts (
	account_id SERIAL PRIMARY KEY,
	user_id INT references Users(user_id) ON DELETE SET NULL,
	balance DECIMAL(10, 2),
	date_created DATE DEFAULT CURRENT_DATE,
	interest DEC(2,2) DEFAULT 0.04,
	role VARCHAR(10) CHECK(role IN ('Checkings', 'Savings'))
);

CREATE TABLE Transactions (
	transaction_id SERIAL PRIMARY KEY,
	from_account_id int REFERENCES Accounts(account_id),
	to_account_id INT REFERENCES Accounts(account_id),
	amount DECIMAL(10, 2),
	date_sent TIMESTAMP 
);

CREATE TABLE PendingTransactions (
    id SERIAL PRIMARY KEY,
    from_account_id INT,
    to_account_id INT,
    amount NUMERIC,
    date_sent TIMESTAMP,
    -- Add any extra columns as needed
    status TEXT DEFAULT 'pending'
);


