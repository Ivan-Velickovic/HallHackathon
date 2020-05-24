from app import db
from datetime import datetime
from models.society import host

class Attendance(db.Model):
    __tablename__ = 'attend'

    eventID = db.Column(db.Text, db.ForeignKey('events.id'), primary_key=True)
    zID = db.Column(db.Text, db.ForeignKey('users.zID'), primary_key=True)
    time = db.Column(db.DateTime(timezone=True), nullable=False)

    user = db.relationship("Users", back_populates="attended")
    event = db.relationship("Event", back_populates="attendees")

    def jsonifySelf(self):
        return {
            'zID': self.zID,
            'time': str(self.time),
            'firstname': self.user.firstname,
            'lastname': self.user.lastname
        }

interest = db.Table('interested',
    db.Column('zID', db.Text, db.ForeignKey('users.zID'), primary_key=True),
    db.Column('eventID', db.Text, db.ForeignKey('events.id'), primary_key=True)
)


# TODO: Need a relationship to hook up compositeEvent with societies
class CompositeEvent(db.Model):
    __tablename__ = "compositeEvents"

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    start = db.Column(db.DateTime(timezone=True), nullable=False)
    end = db.Column(db.DateTime(timezone=True), nullable=False)

    photos = db.Column(db.ARRAY(db.Text), nullable=True)
    description = db.Column(db.Text, nullable=True)
    preview = db.Column(db.Text, nullable=True)
    location = db.Column(db.Text, nullable=True)

    # TODO: Add a relationshipo to connect requests
    # Requests is when a society asks another society to include this event
    # As part of the composite event
    #requests = db.Column(db.ARRAY(db.Text), nullable=True)
    
    status = db.Column(db.Text, nullable=False)
    tags = db.Column(db.ARRAY(db.Text), nullable=True)

    _events = db.relationship("Event", back_populates="_composite")

    def getEvents(self):
        """
        Function to return all the events which belong to this composite event
        """
        return self._events

    def getEventsIDs(self):
        ids = []
        for i in self._events:
            ids.append(i.id)

        return ids

    def getEventsPreview(self):
        previews = []
        for i in self._events:
            previews.append(i.getPreview())

        return previews



class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    start = db.Column(db.DateTime(timezone=True), nullable=False)
    end = db.Column(db.DateTime(timezone=True), nullable=False)

    photos = db.Column(db.ARRAY(db.Text), nullable=True)
    description = db.Column(db.Text, nullable=True)
    preview = db.Column(db.Text, nullable=True)
    location = db.Column(db.Text, nullable=True)

    hasQR = db.Column(db.Boolean, nullable=False)
    hasAccessCode = db.Column(db.Boolean, nullable=False)
    accessCode = db.Column(db.Text, nullable=True)
    hasAdminSignin = db.Column(db.Boolean, nullable=False)

    tags = db.Column(db.ARRAY(db.Integer), nullable=True)

    status = db.Column(db.Integer, nullable=False)

    compositeID = db.Column(db.Text, db.ForeignKey("compositeEvents.id"), nullable=False)
    _composite = db.relationship("CompositeEvent", back_populates="_events")

    attendees = db.relationship("Attendance", back_populates="event")
    #attendances = db.relationship("Attendance")
    interested = db.relationship(
        'Users',
        secondary=interest,
        back_populates="interested"
    )
    hosting = db.relationship(
        'Societies',
        secondary=host,
        back_populates="hosting"
    )

    def getPreview(self):
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.photos[0] if self.photos else None,
            'preview': self.preview,
            'startTime': self.start,
            'location': self.location
        }

    def addAttendance(self, student):
        # TODO: Check whether current time is beyond the ending time
        if self.status == "closed":
            return "Event Closed"
        elif Attendance.query.filter_by(user=student, event=self).first():
            return "Already Attended"

        attend = Attendance(time=datetime.utcnow(),
            user=student, event=self)

        db.session.add(attend)
        db.session.commit()

    def addInterested(self, student):
        self.interested.append(student)

        db.session.add(self)
        db.session.commit()

    def getAttendedCSV(self):
        results = [i.jsonifySelf() for i in self.attendees]
        # TODO: COnver this to a CSV file, save it on the local directory and then
        # Serve up the path
        return results

    def getAttended(self):
        """
        Returns a list of objects of type Users that have attended this event
        """
        return [i for i in self.attendees]

    def getInterested(self):
        """
        Returns a list of objects of type Users that has expressed interest in this event
        """
        return [i for i in self.interested]

    def closeEvent(self):
        self.status = "closed"

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getEventsByTag(tag):
        return 0

    @staticmethod
    def findEvent(id):
        event = Event.query.filter_by(id=id).first()
        return None if not event else event