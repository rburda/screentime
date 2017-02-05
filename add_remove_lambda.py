"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from Users import *
from Requests import *

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

    req = Request(event)

    if req.getType() == "LaunchRequest":
        return on_launch(req)
    elif req.getType() == "IntentRequest":
        return on_intent(req)


#
# Called when the user launches the skill without specifying what they want
#
def on_launch(req):
    print("on_launch requestId=" + req.getRequestId() + ", sessionId=" + req.getSessionId())

    # Dispatch to your skill's launch
    return get_welcome_response(req)


#
# Called when the user specifies an intent for this skill
#
def on_intent(req):
    print("on_intent requestId=" + req.getRequestId() + ", sessionId=" + req.getSessionId())

    # Dispatch to your skill's intent handlers
    if req.getIntent() == "AddTime":
        return add_time(req)
    elif req.getIntent() == "StartTime":
        return start_time(req)
    elif req.getIntent() == "EndTime":
        return end_time(req)
    elif req.getIntent() == "RemoveTime":
        return remove_time(req)
    elif req.getIntent() == "GetCurrentTime":
        return get_current_time(req)
    elif req.getIntent() == "AMAZON.HelpIntent":
        return get_welcome_response(req)
    elif req.getIntent() == "AMAZON.CancelIntent" or req.getIntent() == "AMAZON.StopIntent":
        return handle_session_end_request(req)
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


def build_response(speechlet_response, req):
    req.save_state_in_session()
    return {
        'version': '1.0',
        'sessionAttributes': req.get_session_attributes(),
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response(req):

    card_title = "Welcome"
    speech_output = "Ok."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please say Start screen time for Avery"

    should_end_session = False

    return build_response(build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session), req)


def handle_session_end_request(req):
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. Have a nice day! "
    return build_response(build_speechlet_response(card_title, speech_output, None, True), req)


def start_time(req):
    user_name = req.getUser()
    if user_name == {} or user_name is None:
        return build_response(build_speechlet_response('StartTime', "Who's time is starting?", "", False), req)

    print("User = {}".format(user_name))
    try:
        user = User(user_name)
    except UserNotFoundException:
        return build_response(
            build_speechlet_response('StartTime', '{} is not configured to use screentime'.format(user_name), "", True),
            req)

    if user.has_started_time():
        s_time = user.get_screen_time_start()
        return build_response(
            build_speechlet_response('StartTime',
                                     "{} has already started using screen time at {} {}".format(user_name, s_time.hour,
                                                                                                s_time.minute),
                                     "", True), req)
    user.start_screen_time()
    user.write()
    s_time = user.get_screen_time_start()

    return build_response(
        build_speechlet_response('StartTime',
                                 "Ok. {} has started screen time at {} {}".format(user_name, s_time.hour,
                                                                                  s_time.minute),
                                 "", True), req)


def end_time(req):
    user_name = req.getUser()
    if user_name == {} or user_name is None:
        req.store_slots_in_session()
        return build_response(build_speechlet_response('EndTime', "Who's time is ending?", "", False), req)

    print("User = {}".format(user_name))
    try:
        user = User(user_name)
    except UserNotFoundException:
        return build_response(
            build_speechlet_response('EndTime', '{} is not configured to use screentime'.format(user_name), "", True),
            req)

    if not user.has_started_time():
        return build_response(
            build_speechlet_response('EndTime', "{} did not start using screen time".format(user_name), "", True), req)

    used_time = user.end_screen_time()
    remaining_time = __output_remaining_time(user.get_banked_time())
    response_text = "Ok. {} used {} hours and {} minutes of screentime and has {} available"
    response_text = response_text.format(user_name, used_time.hours, used_time.minutes, remaining_time)
    user.write()
    return build_response(build_speechlet_response('EndTime', response_text, "", True), req)


def add_time(req):
    amount = req.getAmount()
    user_name = req.getUser()

    if amount == {} or amount is None:
        return build_response(
            build_speechlet_response('AddTime', "I'm sorry, I didn't understand how much time to add", "", False), req)
    if user_name == {} or user_name is None:
        return build_response(
            build_speechlet_response('AddTime', "I'm sorry, I didn't understand who to add the time to", "", False),
            req)

    print("User = {}, amount = {}".format(user_name, amount))
    try:
        user = User(user_name)
    except UserNotFoundException:
        return build_response(
            build_speechlet_response('AddTime', "I'm sorry, I didn't understand who to add the time to", "", False),
            req)

    user.add_banked_time(amount)
    user.write()

    banked_time = __output_remaining_time(user.get_banked_time())
    speech_output = 'Done. {} now has {} screen time available'.format(user_name, banked_time)
    return build_response(build_speechlet_response('AddTime', speech_output, '', True), req)


def remove_time(req):
    amount = req.getAmount()
    user_name = req.getUser()

    if amount == {} or amount is None:
        return build_response(
            build_speechlet_response('RemoveTime', "I'm sorry, I didn't understand how much time to remove", "",
                                     False), req)
    if user_name == {} or user_name is None:
        return build_response(
            build_speechlet_response('RemoveTime', "I'm sorry, I didn't understand who to remove the time from", "",
                                     False), req)

    print("User = {}, amount = {}".format(user_name, amount))
    try:
        user = User(user_name)
    except UserNotFoundException:
        return build_response(
            build_speechlet_response('RemoveTime', "I'm sorry, I didn't understand who to remove the time from", "",
                                     False), req)

    user.remove_banked_time(amount)
    user.write()

    banked_time = __output_remaining_time(user.get_banked_time())
    speech_output = 'Done. {} now has {} screen time available'.format(user_name, banked_time)
    return build_response(build_speechlet_response('RemoveTime', speech_output, '', True), req)


def get_current_time(req):
    user_name = req.getUser()

    if user_name == {} or user_name is None:
        return build_response(
            build_speechlet_response('GetCurrentTime',
                                     "I'm sorry, I didn't understand who to get the current screen time for", "",
                                     False), req)

    print("User = {}".format(user_name))
    try:
        user = User(user_name)
    except UserNotFoundException:
        return build_response(
            build_speechlet_response('GetCurrentTime',
                                     "I'm sorry, I didn't understand who to get the current screen time for", "",
                                     False), req)

    banked_time = __output_remaining_time(user.get_banked_time())
    speech_output = '{} has {} screen time available'.format(user_name, banked_time)
    return build_response(build_speechlet_response('GetCurrentTime', speech_output, '', True), req)


def __output_remaining_time(val):
    output = ""
    if val.days > 0:
        output = output + " {} days".format(val.days)
    if val.hours > 0:
        output = output + " {} hours".format(val.hours)
    if val.minutes > 0:
        output = output + " and {} minutes".format(val.minutes)

    if output is "":
        output = "zero"
    return output
