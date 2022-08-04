CREATE TABLE IF NOT EXISTS artists (
    id VARCHAR(20),
    name VARCHAR(50),
    followers INT,
    popularity INT,
    url VARCHAR(100)
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS tracks (
    id VARCHAR(20),
    name VARCHAR(50),
    artist_id VARCHAR(20),
    duration TIME
    PRIMARY KEY (id),
    FOREIGN KEY (artists.id, artist_id)
);

CREATE TABLE IF NOT EXISTS listens (
    track_id VARCHAR(20),
    artist_id VARCHAR(20),
    time_played DATETIME,
    duration_playes TIME
    FOREIGN KEY (tracks.id, tracks_id),
    FOREIGN KEY (artists.id, artist_id)
);