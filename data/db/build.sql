CREATE TABLE IF NOT EXISTS guild(
    VouchChannel int DEFAULT 0
);

CREATE TABLE IF NOT EXISTS vouch(
    UserID integer PRIMARY KEY,
    Vouches integer DEFAULT 0
);