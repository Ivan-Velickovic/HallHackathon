from util.utilFunctions import createConnection, checkUser, checkEvent
from util.societies import findSocID
from util.users import createUser
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

# NOTE: The dict below is for the "onThisWeek" statistics
# NOTE: CHANGE THE EVENT TABLE TO INCLUDE THE WEEK 
# FIXME: FIXME WHEN IT COMES TO 2021
week = datetime.strptime('2020-02-17', "%Y-%m-%d").date()
weekDate = {}
for counter in range(1, 12):
    weekDate[f'T1W{str(counter)}'] = str(week)
    week += relativedelta(days=7)

week = datetime.strptime('2020-06-01', "%Y-%m-%d").date()
for counter in range(1, 12):
    weekDate[f'T2W{str(counter)}'] = str(week)
    week += relativedelta(days=7)

week = datetime.strptime('2020-09-14', "%Y-%m-%d").date()
for counter in range(1, 12):
    weekDate[f'T3W{str(counter)}'] = str(week)
    week += relativedelta(days=7)

def findWeek(date: datetime):
    previousI = 0
    for i in weekDate.keys():
        currWeek = datetime.strptime(weekDate[i], "%Y-%m-%d").date()
        if (date < currWeek):
            if (previousI == 0):
                return None
            return previousI

        previousI = i
    return None


# Creting an event (single instance events)
def createSingleEvent(zID, eventID, eventName, eventDate, qrFlag, societyID, location = None, description = None, endTime = None):
    conn = createConnection()
    curs = conn.cursor()

    if (checkUser(zID) == False):
        return "no such user"
    else:
        curs.execute("SELECT * FROM socStaff WHERE society = (%s) AND zid = (%s) AND role = 1;", (societyID, zID,))
        results = curs.fetchone()
        if (results is None):
            return "not an admin"

    if (checkEvent(eventID) != False):
        return "already exists"
    elif (societyID == None):
        # NOTE: Currently, defaults to UNSW Hall
        societyID = findSocID("UNSW Hall")

    eventDate = datetime.strptime(eventDate, "%Y-%m-%d").date()
    week = findWeek(eventDate)
    if (week == None):
        return "Not a valid date for events"

    curs.execute("INSERT INTO events(eventID, name, owner, eventDate, eventWeek, qrCode, description, endTime) VALUES ((%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s));", (eventID, eventName, zID, eventDate, week, qrFlag, description, endTime,))

    # NOTE: Currently, location defaults to UNSW Hall if one isnt provided
    curs.execute("INSERT INTO host(location, society, eventID) VALUES ((%s), (%s), (%s));", ("UNSW Hall" if location is None else location, societyID if societyID is not None else -1, eventID,))
    conn.commit()
    conn.close()
    return eventID, True

'''
    # Creating a recurring event (need specification on what kind of recurrence)
    # Currently, accept four different recurrent parametres, startDate and endDate to indicate how muuch this recurrence will be
    # recurType indicates what kind of recurrence this is (accepts: "day", "week", "month")
    # recurInterval indicates how many of said recurType is inbetween each interval (accepts any int less than 365)
    # Example: startDate = 2020-01-30, endDate = 2020-05-30, recurType = "day", recurInterval = 14 
    # Example Cont.: The above indicates this event occurs every fortnightly starting with 30/1/2020 to 30/5/2020
'''
def createRecurrentEvent(zID, eventID, eventName, eventStartDate, eventEndDate, recurInterval, recurType, qrFlag = None, location = None, societyID = None, description = None, endTime = None):
    conn = createConnection()
    curs = conn.cursor()

    if (checkUser(zID) == False):
        conn.close()
        return "no such user"
    else:
        curs.execute("SELECT * FROM socStaff WHERE society = (%s) AND zid = (%s) AND role = 1;", (societyID, zID,))
        results = curs.fetchone()
        if (results is None):
            conn.close()
            return "not an adminsuch user"

    if (checkEvent(eventID) != False):
        conn.close()
        return "Event already exists"
    elif (societyID == None):
        societyID = findSocID("UNSW Hall")

    interval = None
    recurInterval = int(recurInterval)
    if (recurType == "day"):
        interval = relativedelta(days=recurInterval)
    elif (recurType == "week"):
        interval = relativedelta(weeks=recurInterval)
    elif (recurType == "month"):
        interval = relativedelta(months=recurInterval)
    else:
        conn.close()
        return "Unacceptable parametre"

    eventStartDate = datetime.strptime(eventStartDate, "%Y-%m-%d").date()
    eventEndDate = datetime.strptime(eventEndDate, "%Y-%m-%d").date()
    counter = 0
    eventIDLists = []
    previousWeek = None
    while eventStartDate < eventEndDate:
        currEventID = eventID + f"{counter:05d}"
        week = findWeek(eventStartDate)
        if (week is None):
            break
        elif (previousWeek == week):
            eventStartDate += interval
            continue

        try:
            curs.execute("INSERT INTO events(eventID, name, owner, eventDate, eventWeek, qrCode, description, endTime) VALUES ((%s), (%s), (%s), (%s), (%s), (%s), (%s), (%s));", (currEventID, eventName, zID, eventStartDate, week, qrFlag, description, endTime,))

            curs.execute("INSERT INTO host(location, society, eventID) VALUES ((%s), (%s), (%s));", ("UNSW Hall" if location is None else location, societyID if societyID is not None else -1, currEventID,))

            eventIDLists.append({"date": str(eventStartDate), "eventID": currEventID})
        except Exception as e:
            conn.commit()
            return "Error encountered"
        eventStartDate += interval
        counter += 1
        previousWeek = week
    conn.commit()
    conn.close()

    return eventIDLists, True

# Returns a set of attendance numbers for each events
def fetchRecur(eventID):
    baseID = eventID[:5]
    print(baseID)

    conn = createConnection()
    curs = conn.cursor()
    curs.execute(f"select * from events where eventID like '{baseID}%';")
    results = curs.fetchall()
    payload = []
    for event in results:
        eventJSON = {}
        eventJSON['eventID'] = event[0]
        eventJSON['name'] = event[1]
        eventJSON['date'] = str(event[2])

        curs.execute("select count(*) as count from participation where eventID = (%s);", (event[0],))
        eventJSON['attendance'] = curs.fetchone()[0]

        payload.append(eventJSON)
    conn.close()
    return payload

def getEndTime(eventID):
    conn = createConnection()
    curs = conn.cursor()

    try:
        curs.execute("SELECT endTime FROM EVENTS WHERE EVENTID = (%s);", (eventID,))
    except Exception as e:
        return None

    result = curs.fetchone()[0]
    return result

def getAllEvents():
    conn = createConnection()
    curs = conn.cursor()

    currentDate = datetime.now().date()
    currentDate = str(currentDate)
    try:
        curs.execute("SELECT eventID, name, eventDate FROM events WHERE eventDate > (%s);", (currentDate, ))
    except Exception as e:
        return None
    
    results = curs.fetchall()
    if results == []:
        return None

    payload = []
    for result in results:
        eventJSON = {}
        eventJSON['eventID'] = result[0]
        eventJSON['name'] = result[1]
        eventJSON['eventDate'] = result[2]
        payload.append(eventJSON)
    return payload