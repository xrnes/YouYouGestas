CREATE TABLE IF NOT EXISTS listening_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    artist TEXT NOT NULL,
    album TEXT,
    title TEXT NOT NULL,
    duration INTEGER,
    played INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS stats_cache (
    period TEXT,
    type TEXT,
    data TEXT,
    updated DATETIME
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON listening_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_artist ON listening_history(artist);
CREATE INDEX IF NOT EXISTS idx_artist_date ON listening_history(artist, date(timestamp));
