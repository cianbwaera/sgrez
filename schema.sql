CREATE TABLE IF NOT EXISTS commands (
    num BIGINT NOT NULL DEFAULT 0
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



CREATE TABLE IF NOT EXISTS blacklisted_guilds (
    guild_id BIGINT PRIMARY KEY,
    result TEXT -- some random thing
)