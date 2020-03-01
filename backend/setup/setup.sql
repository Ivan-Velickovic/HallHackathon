-- drop TABLE IF EXISTS users CASCADE;
CREATE TABLE IF NOT EXISTS users (
    zid TEXT NOT NULL,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    isArc BOOLEAN NOT NULL,
    commencementYear INTEGER NOT NULL,
    studentType TEXT NOT NULL,
    degreeType TEXT NOT NULL,
    activationLink TEXT,
    activationStatus BOOLEAN NOT NULL,
    primary key(zid)
);
-- drop TABLE IF EXISTS events CASCADE;
CREATE TABLE IF NOT EXISTS events (
    eventID TEXT NOT NULL,
    name TEXT NOT NULL,
    eventdate date NOT NULL,
    --- NOTE: FIXME: Added in a starttime in events, this is used to ensure users cant sign in to events before/after the event
    --- NOTE: We could, however, also add in a "grace period" of which we allow people to sign up (i.e. 30 mins before/after)
    startTime time,
    endTime time,
	eventWeek TEXT NOT NULL,
    owner TEXT NOT NULL REFERENCES users(zid),
    qrCode boolean,
    description TEXT,
 primary key(eventID)
);
-- drop TABLE IF EXISTS participation CASCADE;
CREATE TABLE IF NOT EXISTS participation (
    points TEXT NOT NULL,
    isArcMember boolean NOT NULL,
    zid TEXT NOT NULL REFERENCES users(zid),
    eventID TEXT NOT NULL REFERENCES events(eventID),
    time timestamp NOT NULL,
    primary key (zid, eventID)
);
-- drop TABLE IF EXISTS society CASCADE;
CREATE TABLE IF NOT EXISTS society (
    societyID TEXT,
    societyName TEXT NOT NULL unique,
    primary key (societyID)
);
-- drop TABLE IF EXISTS host CASCADE;
CREATE TABLE IF NOT EXISTS host (
    location TEXT,
    society TEXT REFERENCES society(societyID),
    eventID TEXT NOT NULL REFERENCES events(eventID),
    primary key (society, eventID)
);
-- drop TABLE IF EXISTS socstaff CASCADE;
CREATE TABLE IF NOT EXISTS socstaff (
    society TEXT REFERENCES society(societyID),
    zid TEXT REFERENCES users(zid),
    role INTEGER NOT NULL,
    primary key (society, zid)
);

create or replace view hostedEvents 
as select events.eventID, name, eventdate, location, societyname, societyID from events 
join host on events.eventID = host.eventID join society on (society.societyID = host.society);

create or replace view userInSociety 
as select societyid, societyname, users.zID, role from society 
join socstaff on society.societyid = socstaff.society join users on socstaff.zid = users.zid;

create or replace view userParticipatedEvents 
as select hostedEvents.eventID, name, eventdate, location, hostedevents.societyname, societyid, zid from hostedEvents
join participation ON hostedEvents.eventID = participation.eventID;