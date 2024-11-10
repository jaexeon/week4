CREATE TABLE post_table (
    post_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    post_user VARCHAR(40) NOT NULL,
    post_password VARCHAR(100) NOT NULL,
    post_title VARCHAR(50) NOT NULL,
    post_content VARCHAR(200) NOT NULL,
    post_date DATETIME NOT NULL,
    post_view_cnt INT NOT NULL DEFAULT 0,
    post_is_secret INT NOT NULL DEFAULT 0
) DEFAULT CHARSET=UTF8;

CREATE TABLE user_table (
    user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(40) NOT NULL,
    user_password VARCHAR(100) NOT NULL
) DEFAULT CHARSET=UTF8;

CREATE TABLE comment_table (
    comment_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    comment_parent_post_id INT NOT NULL,
    comment_user VARCHAR(40) NOT NULL,
    comment_password VARCHAR(100) NOT NULL,
    comment_content VARCHAR(1000) NOT NULL
) DEFAULT CHARSET=UTF8;

INSERT INTO post_table(post_user, post_password, post_title, post_content, post_is_secret, post_date) VALUES('Anonymous', '1234', 'example_title', 'example_content', 0, now());