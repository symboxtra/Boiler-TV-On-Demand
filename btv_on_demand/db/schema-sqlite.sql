PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY,
    ext_category_id INTEGER,
    name TEXT UNIQUE NOT NULL,
    first_seen TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Some of these fields are random and may have limited value
-- I just grabbed whatever looked interesting in their API response
CREATE TABLE IF NOT EXISTS content (
    id INTEGER PRIMARY KEY,
    ext_content_id TEXT,
    media_item_id TEXT,
    film_id TEXT,
    permalink_token TEXT,
    watchlink_token TEXT,
    content_ordinal INTEGER,
    program_type TEXT,
    title TEXT NOT NULL,
    description TEXT,
    release_year INTEGER,
    runtime_s INTEGER,
    runtime_h REAL,
    content_language TEXT,
    mpaa_rating TEXT,
    ustv_rating TEXT,
    encode_type TEXT,
    license_start TEXT,
    license_end TEXT,
    first_seen TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (ext_content_id, title)
);

CREATE TABLE IF NOT EXISTS person (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS category_content (
    content_id INTEGER REFERENCES content(id),
    category_id INTEGER REFERENCES category(id),
    PRIMARY KEY (content_id, category_id)
);

CREATE TABLE IF NOT EXISTS starring (
    content_id INTEGER REFERENCES content(id),
    person_id INTEGER REFERENCES person(id),
    PRIMARY KEY (content_id, person_id)
);

CREATE TABLE IF NOT EXISTS directed_by (
    content_id INTEGER REFERENCES content(id),
    person_id INTEGER REFERENCES person(id),
    PRIMARY KEY (content_id, person_id)
);

-- Licensing history
CREATE TABLE IF NOT EXISTS license (
    id INTEGER PRIMARY KEY,
    content_id INTEGER REFERENCES content(id),
    license_start TEXT,
    license_end TEXT,
    UNIQUE (content_id, license_start, license_end)
);


DROP VIEW IF EXISTS current_content;
CREATE VIEW current_content AS
    SELECT
        *
    FROM content
    WHERE license_end >= datetime('now')
;

DROP VIEW IF EXISTS expired_content;
CREATE VIEW expired_content AS
    SELECT
        *
    FROM content
    WHERE license_end < datetime('now')
;