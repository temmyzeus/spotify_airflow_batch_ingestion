CREATE TABLE IF NOT EXISTS artists (
    id VARCHAR(23) NOT NULL,
    name VARCHAR(50) NOT NULL,
    genre VARCHAR(500),
    followers INT NOT NULL,
    -- Spotify uses a popularity index 0-100
    popularity SMALLINT NOT NULL,
    url VARCHAR,
    PRIMARY KEY (id),
    CHECK (
        popularity >= 0
        AND popularity <= 100
    )
);
CREATE TABLE IF NOT EXISTS tracks (
    id VARCHAR(23) NOT NULL,
    name VARCHAR NOT NULL,
    artist_id VARCHAR(23) NOT NULL,
    duration_ms INTEGER NOT NULL,
    popularity SMALLINT NOT NULL,
    is_in_album BOOLEAN,
    is_explicit BOOLEAN,
    external_url VARCHAR,
    PRIMARY KEY (id),
    CONSTRAINT fk_artist_id FOREIGN KEY (artist_id) REFERENCES artists(id),
    CHECK (
        popularity >= 0
        AND popularity <= 100
    )
);
CREATE TABLE IF NOT EXISTS listens (
    track_id VARCHAR(23),
    artist_id VARCHAR(23),
    time_played TIMESTAMP,
    play_duration_ms INTEGER,
    CONSTRAINT fk_track_id FOREIGN KEY(track_id) REFERENCES tracks(id),
    CONSTRAINT fk_artist_id FOREIGN KEY(artist_id) REFERENCES artists(id)
);
