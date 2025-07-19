CREATE TABLE Users (
	user_id SERIAL PRIMARY KEY,
	first_name TEXT,
	last_name TEXT,
	street TEXT,
	city TEXT,
	st TEXT,
	zip_code TEXT,
	balance DECIMAL(10, 2),
	date_created DATE,
	role VARCHAR(10) CHECK(role IN('Empl', 'User', 'Admin')),
	username VARCHAR(30),
	pw VARCHAR(30)
);


Create Table Accounts (
	account_id SERIAL PRIMARY KEY,
	user_id INT references Users(user_id),
	balance DECIMAL(10, 2),
	date_created DATE,
	interest DEC(2,2),
	role VARCHAR(10) CHECK(role IN ('Checkings', 'Savings'))
);

CREATE TABLE Transactions (
	transaction_id SERIAL PRIMARY KEY,
	from_account_id int REFERENCES Accounts(account_id),
	to_account_id INT REFERENCES Accounts(account_id),
	amount DECIMAL(10, 2),
	date_sent TIMESTAMP 
);

Create Table Loans ( 
	loan_id SERIAL PRIMARY KEY,
	amount DECIMAL(10, 2),
	interest_rate DECIMAL(3, 2),
	loanee INT references Users(user_id)
)