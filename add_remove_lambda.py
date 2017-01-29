"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import boto3
import Users


s3_client = boto3.client('s3')

# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" + event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


# --------------- Events ------------------
#
# Called when the session starts
#
def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])


#
#Called when the user ends the session. Is not called when the skill returns should_end_session=true
#
def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])

#
#Called when the user launches the skill without specifying what they want
#
def on_launch(launch_request, session):

    print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])

    # Dispatch to your skill's launch
    return get_welcome_response()


#
# Called when the user specifies an intent for this skill
#
def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AddTime":
        return add_time(intent)
    elif intent_name == "StartTime":
        return start_time(intent)
    elif intent_name == "EndTime":
        return end_time(intent)
    elif intent_name == "RemoveTime":
        return remove_time(intent)
    elif intent_name == "GetCurrentTime":
        return get_current_time(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': {},
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}

    card_title = "Welcome"
    speech_output = "Ok."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please say Start screen time for Avery"

    should_end_session = False

    return build_response(build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. Have a nice day! "

    # Setting this to true ends the session and exits the skill.
    should_end_session = True

    return build_response(build_speechlet_response(card_title, speech_output, None, should_end_session))


def start_time(intent):
    userName = getSlotValue(intent, "user")
    if userName == {} or userName is None:
        return build_response(build_speechlet_response('StartTime', "Who's time is starting?", "", False))

    print("User = {}".format(userName))
    try:
        user = Users.User(userName)
    except Users.UserNotFoundException:
        return build_response(
            build_speechlet_response('StartTime', '{} is not configured to use screentime'.format(userName), "", True))

    if (user.has_started_time()):
        sTime = user.get_screen_time_start()
        return build_response(
            build_speechlet_response('StartTime',
                                     "{} has already started using screen time at {} {}".format(userName,sTime.hour,sTime.minute),
                                     "", True))
    user.start_screen_time()
    user.write()
    sTime = user.get_screen_time_start()

    return build_response(
        build_speechlet_response('StartTime',
                                 "Ok. {} has started screen time at {} {}".format(userName, sTime.hour, sTime.minute),
                                 "", True))

def end_time(intent):
    userName = getSlotValue(intent, "user")
    if userName == {} or userName is None:
        return build_response(build_speechlet_response('EndTime', "Who's time is ending?", "", False))

    print("User = {}".format(userName))
    try:
        user = Users.User(userName)
    except Users.UserNotFoundException:
        return build_response(
            build_speechlet_response('EndTime', '{} is not configured to use screentime'.format(userName), "", True))

    if not user.has_started_time():
        return build_response(
            build_speechlet_response('EndTime', "{} did not start using screen time".format(userName), "", True))

    usedTime = user.end_screen_time()
    remainingTime = __output_remaining_time(user.get_banked_time())
    responseText = "Ok. {} used {} hours and {} minutes of screentime and has {} available"
    responseText = responseText.format(userName, usedTime.hours, usedTime.minutes, remainingTime)
    user.write()
    return build_response(build_speechlet_response('EndTime',responseText , "", True))


def add_time(intent):
    amount = getSlotValue(intent, "amount")
    userName = getSlotValue(intent, "user")

    if amount == {} or amount is None:
        return build_response(
            build_speechlet_response('AddTime',"I'm sorry, I didn't understand how much time to add", "", False))
    if userName == {} or userName is None:
        return build_response(
            build_speechlet_response('AddTime',"I'm sorry, I didn't understand who to add the time to", "", False))

    print("User = {}, amount = {}".format(userName, amount))
    try:
        user = Users.User(userName)
    except Users.UserNotFoundException:
        return build_response(
            build_speechlet_response('AddTime',"I'm sorry, I didn't understand who to add the time to", "", False))

    user.add_banked_time(amount)
    user.write()

    bankedTime = __output_remaining_time(user.get_banked_time())
    speechOutput = 'Done. {} now has {} screen time available'.format(userName, bankedTime)
    return build_response(build_speechlet_response('AddTime', speechOutput, '', True))

def remove_time(intent):
    amount = getSlotValue(intent, "amount")
    userName = getSlotValue(intent, "user")

    if amount == {} or amount is None:
        return build_response(
            build_speechlet_response('RemoveTime',"I'm sorry, I didn't understand how much time to remove", "", False))
    if userName == {} or userName is None:
        return build_response(
            build_speechlet_response('RemoveTime',"I'm sorry, I didn't understand who to remove the time from", "", False))

    print("User = {}, amount = {}".format(userName, amount))
    try:
        user = Users.User(userName)
    except Users.UserNotFoundException:
        return build_response(
            build_speechlet_response('RemoveTime',"I'm sorry, I didn't understand who to remove the time from", "", False))

    user.remove_banked_time(amount)
    user.write()

    bankedTime = __output_remaining_time(user.get_banked_time())
    speechOutput = 'Done. {} now has {} screen time available'.format(userName, bankedTime)
    return build_response(build_speechlet_response('RemoveTime', speechOutput, '', True))

def get_current_time(intent):
    userName = getSlotValue(intent, "user")

    if userName == {} or userName is None:
        return build_response(
            build_speechlet_response('GetCurrentTime',"I'm sorry, I didn't understand who to get the current screen time for", "", False))

    print("User = {}".format(userName))
    try:
        user = Users.User(userName)
    except Users.UserNotFoundException:
        return build_response(
            build_speechlet_response('GetCurrentTime',"I'm sorry, I didn't understand who to get the current screen time for", "", False))

    bankedTime = __output_remaining_time(user.get_banked_time())
    speechOutput = '{} has {} screen time available'.format(userName, bankedTime)
    return build_response(build_speechlet_response('RemoveTime', speechOutput, '', True))

def getSlotValue(intent, slotName):
    return intent.get("slots", {}).get(slotName, {}).get("value")

def __output_remaining_time(val):
    output = ""
    if (val.days > 0):
        output = output + " {} days".format(val.days)
    if (val.hours > 0):
        output = output + " {} hours".format(val.hours)
    if (val.minutes > 0):
        output = output + " and {} minutes".format(val.minutes)
    return output