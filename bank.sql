CREATE TABLE Users (
	user_id SERIAL PRIMARY KEY,
	first_name TEXT,
	last_name TEXT,
	street TEXT,
	city TEXT,
	state TEXT,
	zip_code TEXT,
	balance DECIMAL(10, 2),
	date_created DATE,
	role VARCHAR(10) CHECK(role IN('Empl', 'User', 'Admin'))
);

CREATE TABLE Transactions (
	transaction_id SERIAL PRIMARY KEY,
	from_user_id int REFERENCES users(user_id),
	to_user_id INT REFERENCES users(user_id),
	amount DECIMAL(10, 2),
	date_sent DATE
);


