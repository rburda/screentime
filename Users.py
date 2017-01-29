import json
import boto3
import datetime
import isodate
import dateutil.parser
import dateutil.relativedelta

class User:

    __currentSession = 'currentSession'
    __time = 'time'
    s3_client = boto3.client('s3')

    def __init__(self, name):
        self.name = name
        self.data = self.__load()

    def write(self):
        User.s3_client.put_object(Bucket='rburda-screentime', Key=self.name, Body=json.dumps(self.data))

    def hasStartedTime(self):
        started = False
        if self.data[User.__currentSession] is not None:
            if self.data[User.__currentSession] != {}:
                if self.data[User.__currentSession] != '-1':
                    started = True
        return started

    def addBankedScreenTime(self, amount):
        current_time = datetime.timedelta(seconds=self.data[User.__time])
        add_time = isodate.parse_duration(amount)
        self.data[User.__time]=(current_time+add_time).total_seconds()

    def removeBankedScreenTime(self, amount):
        current_time = datetime.timedelta(seconds=self.data[User.__time])
        remove_time = isodate.parse_duration(amount)
        self.data[User.__time]=(current_time-remove_time).total_seconds()

    def startScreenTime(self):
        self.data[User.__currentSession]=datetime.datetime.now().isoformat()

    def endScreenTime(self):
        delta = dateutil.relativedelta.relativedelta(datetime.datetime.now(), self.getScreenTimeStart())
        self.removeBankedScreenTime(delta.seconds)
        return delta

    def getScreenTimeStart(self):
        isoFormat = self.data[User.__currentSession]
        return dateutil.parser.parse(isoFormat)

    def getBankedTime(self):
       return dateutil.relativedelta.relativedelta(seconds=self.data[User.__time])

    def __load(self):
        try:
            file = User.s3_clients3_client.get_object(Bucket="rburda-screentime", Key=self.name)
            return json.loads(file.get('Body', {}).read())
        except (Exception):
            raise UserNotFoundException


class UserNotFoundException:
    pass