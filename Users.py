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

    def has_started_time(self):
        started = False
        if self.data[User.__currentSession] is not None:
            if self.data[User.__currentSession] != {}:
                if self.data[User.__currentSession] != '-1':
                    started = True
        return started

    def add_banked_time(self, amount):
        addsecs = self.__parseduration(amount)
        self.data[User.__time]=self.data[User.__time]+addsecs

    def remove_banked_time(self, amount):
        removesecs = self.__parseduration(amount)
        self.data[User.__time]=self.data[User.__time]-removesecs

    def start_screen_time(self):
        self.data[User.__currentSession]=datetime.datetime.now().isoformat()

    def end_screen_time(self):
        delta = dateutil.relativedelta.relativedelta(datetime.datetime.now(), self.get_screen_time_start())
        self.remove_banked_time("P{}DT{}M{}S".format(delta.days, delta.minutes, delta.seconds))
        self.data[User.__currentSession]=None
        return delta

    def get_screen_time_start(self):
        iso_format = self.data[User.__currentSession]
        return dateutil.parser.parse(iso_format)

    def get_banked_time(self):
       return dateutil.relativedelta.relativedelta(seconds=self.data[User.__time])

    def __load(self):
        try:
            file = User.s3_client.get_object(Bucket="rburda-screentime", Key=self.name)
            return json.loads(file.get('Body', {}).read())
        except (Exception):
            raise UserNotFoundException

    def __parseduration(self, val):
        time = isodate.parse_duration(val)

        if (isinstance(time, isodate.duration.Duration)):
            monthsecs = time.months*30*24*60*60
            yearsecs = time.years*12*30*24*60*60
            dursecs = float(monthsecs+yearsecs)+time.total_seconds()
        else:
            dursecs = time.total_seconds()

        return dursecs


class UserNotFoundException:
    pass