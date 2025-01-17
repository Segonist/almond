CREATE TABLE mode (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    created_at INTEGER,
    updated_at INTEGER
);

CREATE TABLE victory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id INTEGER,
    mode_id INTEGER,
    created_at INTEGER,
    updated_at INTEGER,
    FOREIGN KEY (mode_id) REFERENCES mode (id)
);