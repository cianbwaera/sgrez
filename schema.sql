CREATE TABLE IF NOT EXISTS commands (
    num BIGINT NOT NULL,
    id BIGINT PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS bank (
    user_id BIGINT PRIMARY KEY NOT NULL,
    user_money BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS shop (
    role_id BIGINT UNIQUE NOT NULL,
    guild_id BIGINT NOT NULL,
    shop_id TEXT NOT NULL,
    amount BIGINT NOT NULL
);


-- have the schema handle stuff if the table is empty, 342 is not a random number so don't change it!
INSERT INTO commands(num, id) VALUES(0, 342) ON CONFLICT(id) DO NOTHING;

CREATE TABLE IF NOT EXISTS development (
    updates TEXT,
    rid INT NOT NULL PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS giveaways (
    user_id BIGINT,
    coin_award INT
);

CREATE TABLE IF NOT EXISTS prefixes (
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(10)
);