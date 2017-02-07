class Request:

    def __init__(self, json):
        self.request = json.get("request")
        self.session = json.get("session")
        self.sessionId = self.session.get("sessionId")
        self.continuingSession = self.session.get("new")

    def getIntent(self):
        if self.session.get("new") is True:
            return self.request.get("intent").get("name")
        else:
            return self.__get_session_attribute("prevIntent")

    def getRequestId(self):
        return self.request.get("requestId")

    def getSessionId(self):
        return self.session.get("sessionId")

    def getType(self):
        return self.request.get("type")

    def getUser(self):
        if self.__get_slot_value("user") == None:
            return self.__get_session_attribute("user")
        else:
            return self.__get_slot_value("user")

    def getAmount(self):
        if self.__get_slot_value("amount") == None:
            return self.__get_session_attribute("amount")
        else:
            return self.__get_slot_value("amount")

    def save_state_in_session(self):
        self.__store_slots_in_session()
        self.__add_session_attribute("prevIntent", self.getIntent())

    def get_session_attributes(self):
        return self.session.get("attributes",{})

    def __get_slot_value(self, slotName):
        return self.request.get("intent").get("slots", {}).get(slotName, {}).get("value")

    def __store_slots_in_session(self):
        for slotName in self.request.get("intent").get("slots",{}).keys():
            self.__add_session_attribute(slotName, self.__get_slot_value(slotName))

    def __add_session_attribute(self, key, value):
        if (self.session.get("attributes") == None):
            self.session["attributes"]={}
        self.session.get("attributes")[key] = value

    def __get_session_attribute(self, attribName):
        return self.session.get("attributes", {}).get(attribName, {})




"""
First request to add time for user that is not known
{
  "session": {
    "sessionId": "SessionId.bc3b968b-c9df-41c0-9c9c-7dc021ea9555",
    "application": {
      "applicationId": "amzn1.ask.skill.d64fd558-5e27-4d9a-9984-cc4887d864b0"
    },
    "attributes": {},
    "user": {
      "userId": "amzn1.ask.account.AFQ2FD3HGAZMZXXLTKFW5E4KD3BG3R3ASFJPEFOH2UMJPEWENYRBN5J4E7RR6UA7DV3J4O3HJ2YBZG4LKF57MJXTDWFZOVTL2XPRLQI5KZWOIFMEIKSV2NGYU7IEROMJY53NWNMOJS7TQESHPCMNU2JPJEPDPFDQXYXVMFUCQG6NT2JYUYXUUMD6EMEEDIFACYFKZRIWIZ6X6AA"
    },
    "new": true
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "EdwRequestId.2d78fdee-37d8-452b-a5b6-f4fd09f06f68",
    "locale": "en-US",
    "timestamp": "2017-02-03T06:16:19Z",
    "intent": {
      "name": "AddTime",
      "slots": {
        "user": {
          "name": "user",
          "value": "George"
        },
        "amount": {
            "name": "amount",
            "value": "PT1M"
        }
      }
    }
  },
  "version": "1.0"
}

Second Request to Add Time after initial request didn't read user
{
  "session": {
    "sessionId": "SessionId.bc3b968b-c9df-41c0-9c9c-7dc021ea9555",
    "application": {
      "applicationId": "amzn1.ask.skill.d64fd558-5e27-4d9a-9984-cc4887d864b0"
    },
    "attributes": {"user":"George", "amount":"PT1M", "prevIntent":"AddTime"},
    "user": {
      "userId": "amzn1.ask.account.AFQ2FD3HGAZMZXXLTKFW5E4KD3BG3R3ASFJPEFOH2UMJPEWENYRBN5J4E7RR6UA7DV3J4O3HJ2YBZG4LKF57MJXTDWFZOVTL2XPRLQI5KZWOIFMEIKSV2NGYU7IEROMJY53NWNMOJS7TQESHPCMNU2JPJEPDPFDQXYXVMFUCQG6NT2JYUYXUUMD6EMEEDIFACYFKZRIWIZ6X6AA"
    },
    "new": false
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "EdwRequestId.2d78fdee-37d8-452b-a5b6-f4fd09f06f68",
    "locale": "en-US",
    "timestamp": "2017-02-03T06:16:19Z",
    "intent": {
      "name": "GetCurrentTime",
      "slots": {
        "user": {
          "name": "user",
          "value": "Avery"
        }
      }
    }
  },
  "version": "1.0"
}

StartTime Request
{
  "session": {
    "sessionId": "SessionId.bc3b968b-c9df-41c0-9c9c-7dc021ea9555",
    "application": {
      "applicationId": "amzn1.ask.skill.d64fd558-5e27-4d9a-9984-cc4887d864b0"
    },
    "user": {
      "userId": "amzn1.ask.account.AFQ2FD3HGAZMZXXLTKFW5E4KD3BG3R3ASFJPEFOH2UMJPEWENYRBN5J4E7RR6UA7DV3J4O3HJ2YBZG4LKF57MJXTDWFZOVTL2XPRLQI5KZWOIFMEIKSV2NGYU7IEROMJY53NWNMOJS7TQESHPCMNU2JPJEPDPFDQXYXVMFUCQG6NT2JYUYXUUMD6EMEEDIFACYFKZRIWIZ6X6AA"
    },
    "new": true
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "EdwRequestId.2d78fdee-37d8-452b-a5b6-f4fd09f06f68",
    "locale": "en-US",
    "timestamp": "2017-02-03T06:16:19Z",
    "intent": {
      "name": "StartTime",
      "slots": {
        "user": {
          "name": "user",
          "value": "Avery"
        }
      }
    }
  },
  "version": "1.0"
}
"""


