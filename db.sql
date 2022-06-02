CREATE TABLE IF NOT EXISTS channel_store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_channel_id INTEGER NOT NULL,
    discord_channel_name VARCHAR(255) NOT NULL,
    channel_type VARCHAR(255) NOT NULL,
    category_id INTEGER NOT NULL,
    channel_number INTEGER NOT NULL,
    linked_role_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id INTEGER NOT NULL,
    captcha TEXT NOT NULL,
    captcha_passed INTEGER NOT NULL,
)