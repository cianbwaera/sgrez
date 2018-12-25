CREATE TABLE IF NOT EXISTS commands (
    num BIGINT NOT NULL,
    id BIGINT PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS bank (
    user_id BIGINT PRIMARY KEY NOT NULL,
    user_money BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS shop (
    role_id BIGINT UNIQUE NOT NULL,
    guild_id BIGINT NOT NULL,
    shop_num INT NOT NULL,
    amount BIGINT NOT NULL
);


-- have the schema handle stuff if the table is empty
INSERT INTO commands(num, id) VALUES(0, 342) ON CONFLICT(id) DO NOTHING;
