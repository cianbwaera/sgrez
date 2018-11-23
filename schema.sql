-- To hold the command count of the bot, BIGINT is required since it isnt gonna be 1 thru 9 or some shit
CREATE TABLE IF NOT EXISTS commands_used (
    cmdcount BIGINT NOT NULL DEFAULT 0
);
-- Creates the Economy Table
CREATE TABLE IF NOT EXISTS bank (
    user_id BIGINT PRIMARY KEY NOT NULL,
    user_money BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS shop (
    role_id BIGINT UNIQUE NOT NULL,
    guild_id BIGINT PRIMARY KEY NOT NULL,
);

CREATE TABLE IF NOT EXISTS cooldowns (
    user_id BIGINT PRIMARY KEY NOT NULL,
    start_time INT NOT NULL,
    end_time INT NOT NULL
);