CREATE TABLE Users (
	user_id SERIAL PRIMARY KEY,
	first_name VARCHAR(45),
	last_name VARCHAR(45),
	balance INT,
	date_created DATE,
	role VARCHAR(10) CHECK(role IN('Empl', 'User', 'Admin'))
);

CREATE TABLE Transactions (
	transaction_id SERIAL PRIMARY KEY,
	from_user_id int REFERENCES users(user_id),
	to_user_id INT REFERENCES users(user_id),
	amount FLOAT,
	date_sent DATE
);


