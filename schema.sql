-- To hold the command count of the bot, BIGINT is required since it isnt gonna be 1 thru 9 or some shit
CREATE TABLE IF NOT EXISTS pdp_cmds (
    cmdcount BIGINT NOT NULL DEFAULT 0
);
-- Creates the Economy Table
CREATE TABLE IF NOT EXISTS pdp_economy (
    user_id BIGINT PRIMARY KEY NOT NULL,
    user_money BIGINT NOT NULL DEFAULT 0
);