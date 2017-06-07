import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3

region = 'us-east-1'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ec2 = boto3.resource('ec2', region_name=region)
ec2_client = boto3.client('ec2')


# Start an instance
	
def start_instance(intent_request):
	#instances_new = ['i-0694538dcecccd286', 'i-0750818866f582046', 'i-08b13efc08deeab53']
	#ec2.start_instances(InstanceIds=instances_new)
	instance = intent_request['currentIntent']['slots']['Instances']
	print ('HI')
	print (instance)
	return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'The instance you have requested has been started.'
        }
    )
	

		


# Greetings

def greetings(intent_request):
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Hello!! My name is LabRat  How can I help you today?'
        }
    )
	
	
	
def close(fulfillment_state, message):
    response = {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    return response

def elicit(fulfillment_state, message):
    response = {
        'dialogAction': {
            'type': 'ElicitIntent',
            'message': message
        }
    }
    return response	
# --- Intent handler ---
	

def dispatch(intent_request):

	logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
	intent_name = intent_request['currentIntent']['name']
	print(intent_request)
	# Dispatch to your bot's intent handlers
	
	if intent_name == 'Start_Instances':
		return start_instance(intent_request)
	
	else :
		return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'The request which you are looking for does not support with the current release '
					    'Apologise for the inconvenience!!' 'May be we plan it out in the next release'
                      
        }
    )


# --- Main handler ---

def lambda_handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
	os.environ['TZ'] = 'America/New_York'
	time.tzset()
	logger.debug('event.bot.name={}'.format(event['bot']['name']))
	return dispatch(event)