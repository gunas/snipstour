#!/usr/bin/env python2

import ConfigParser
import sys
import io
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import requests
from socketIO_client import SocketIO
socketIO = SocketIO('localhost', 80)
lastcommand = ''
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
     if len(intent_message.slots.TURN_COMMAND_SLOT) > 0:
         turn_command = intent_message.slots.TURN_COMMAND_SLOT.first().value
         socketIO.emit('rotation_command', turn_command)
         lastcommand = 'rotation_command@'+ turn_command
         requests.get('http://localhost/sstore?lastcommand='+ lastcommand + '&sid=' + intent_message.session_id)
         hermes.publish_continue_session(intent_message.session_id, 'Turing '+ turn_command + ', Would you like to do that again?', ['gunasekartr:continueintent']);
     else:
         hermes.publish_end_session(intent_message.session_id, "It doesn't work like that, try again please")

def subscribe_intent_movecommand(hermes, intent_message):
     if len(intent_message.slots.MOVE_COMMAND_SLOT) > 0:
         move_command = intent_message.slots.MOVE_COMMAND_SLOT.first().value
         socketIO.emit('move_command', move_command)
         lastcommand = 'move_command@'+ move_command
         requests.get('http://localhost/sstore?lastcommand='+ lastcommand + '&sid=' + intent_message.session_id)
         hermes.publish_continue_session(intent_message.session_id, 'Moving ' + move_command + ', Would you like to do that again?', ['gunasekartr:continueintent']);
     else:
         hermes.publish_end_session(intent_message.session_id, "It doesn't work like that, try again please")

def subscribe_intent_continue(hermes, intent_message):
     if len(intent_message.slots.YES_NO_SLOT) > 0:
         continue_answer = intent_message.slots.YES_NO_SLOT.first().value
         if continue_answer == 'yes':
             lastcommand = requests.get('http://localhost/lastcommand?sid=' + intent_message.session_id)
             print(lastcommand)
             print(lastcommand.raw)
             print('lastcom:' + lastcommand.text)
             last_intent_command, action = lastcommand.text.split("@")
             socketIO.emit(last_intent_command, action)
             hermes.publish_continue_session(intent_message.session_id, 'Ok, Would you like to do the move again?', ['gunasekartr:continueintent']);
         else:
             hermes.publish_end_session(intent_message.session_id, "That's fine");     
     else:
         hermes.publish_end_session(intent_message.session_id, "Would you like to do the move again?")

if __name__ == "__main__":
    with Hermes('localhost:1883') as h:
        h.subscribe_intent('gunasekartr:turncommandintent', subscribe_intent_turncommand) \
            .subscribe_intent('gunasekartr:movecommandintent', subscribe_intent_movecommand) \
            .subscribe_intent('gunasekartr:continueintent', subscribe_intent_continue) \
            .subscribe_session_ended(session_ended) \
            .subscribe_session_started(session_started) \
            .start()
