#!/usr/bin/env python2

import ConfigParser
import sys
import io
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import requests
from socketIO_client import SocketIO, BaseNamespace
class RotationNamespace(BaseNamespace):

    def on_aaa_response(self, *args):
        print('on_aaa_response', args)

socketIO = SocketIO('192.168.0.104', 80)
rotation_namespace = socketIO.define(ChatNamespace, '/rotation_command')
class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name: option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding='utf-8') as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def session_started(hermes, session_started_message):
    session_id = session_started_message.session_id
    custom_data = session_started_message.custom_data
    sentence = 'Started a new session of' + \
        session_id + ' with data ' + str(custom_data)
    print(sentence)


def session_ended(hermes, session_ended_message):
    session_id = session_ended_message.session_id
    session_site_id = session_ended_message.site_id
    print('Ending session...')
 
def subscribe_intent_turncommand(hermes, intent_message):
     conf = read_configuration_file('config.ini')
     if len(intent_message.slots.TURN_COMMAND_SLOT) > 0:
         turn_command = intent_message.slots.TURN_COMMAND_SLOT.first().value
         rotation_namespace.emit(turn_command)
         hermes.publish_end_session(intent_message.session_id, 'Ok, Moving ' + turn_command)
     else:
         hermes.publish_end_session(intent_message.session_id, "It doesn't work like that, try again please")

if __name__ == "__main__":
    with Hermes('localhost:1883') as h:
        h.subscribe_intent('gunasekartr:turncommandintent', subscribe_intent_turncommand) \
            .subscribe_session_ended(session_ended) \
            .subscribe_session_started(session_started) \
            .start()
