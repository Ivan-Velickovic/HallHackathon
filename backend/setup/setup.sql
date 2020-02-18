drop TABLE IF EXISTS users cascade;
CREATE TABLE IF NOT EXISTS users (
    zid TEXT NOT NULL,
    password TEXT NOT NULL,
    isArc BOOLEAN NOT NULL,
    primary key(zid)
);
drop TABLE IF EXISTS events cascade;
CREATE TABLE IF NOT EXISTS events (
    eventID TEXT NOT NULL,
    name TEXT NOT NULL,
    eventdate date NOT NULL,
	eventWeek TEXT NOT NULL,
    owner TEXT NOT NULL REFERENCES users(zid),
    qrCode boolean,
    description TEXT,
 primary key(eventID)
);
drop TABLE IF EXISTS participation cascade;
CREATE TABLE IF NOT EXISTS participation (
    points TEXT NOT NULL,
    isArcMember boolean NOT NULL,
    zid TEXT NOT NULL REFERENCES users(zid),
    eventID TEXT NOT NULL REFERENCES events(eventID),
    time timestamp NOT NULL,
    primary key (zid, eventID)
);
drop TABLE IF EXISTS society cascade;
CREATE TABLE IF NOT EXISTS society (
    societyID TEXT,
    societyName TEXT NOT NULL unique,
    primary key (societyID)
);
drop TABLE IF EXISTS host cascade;
CREATE TABLE IF NOT EXISTS host (
    location TEXT,
    society TEXT REFERENCES society(societyID),
    eventID TEXT NOT NULL REFERENCES events(eventID),
    primary key (society, eventID)
);
drop TABLE IF EXISTS socstaff cascade;
CREATE TABLE IF NOT EXISTS socstaff (
    society TEXT REFERENCES society(societyID),
    zid TEXT REFERENCES users(zid),
    role INTEGER NOT NULL,
    primary key (society, zid)
);
