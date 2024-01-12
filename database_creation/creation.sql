CREATE DATABASE db_bit_talker;
USE db_bit_talker;

CREATE TABLE IF NOT EXISTS user_info (
	id INT PRIMARY KEY auto_increment,
    name VARCHAR(100),
    username VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(300)
);

CREATE TABLE user_chat (
	sender_id INT,
    receiver_id INT,
    message BLOB,
    message_date DATE,
    message_time TIME,
    is_taken BOOLEAN,
    is_notified BOOLEAN,
    FOREIGN KEY (sender_id) REFERENCES user_info(id),
    FOREIGN KEY (receiver_id) REFERENCES user_info(id)
);
