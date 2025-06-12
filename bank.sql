CREATE TABLE Users (
	user_id SERIAL PRIMARY KEY,
	first_name VARCHAR(45),
	last_name VARCHAR(45),
	balance INT
);

CREATE TABLE Transations (
	transaction_id SERIAL PRIMARY KEY,
	from_user_id int REFERENCES users(user_id),
	to_user_id INT REFERENCES users(user_id),
	sent_num INT,
	date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


