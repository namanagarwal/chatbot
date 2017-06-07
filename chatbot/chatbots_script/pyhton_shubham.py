import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
import re

region = 'us-east-1'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ec2 = boto3.resource('ec2', region_name=region)
ec2_client = boto3.client('ec2')
lex_client = boto3.client('lex-models')


# Start an instance
	
def action_instance(intent_request):
	instance_action = intent_request['currentIntent']['slots']['instance_actions']
	instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
	'''if instance_identifier is None:
	    response_get_slot_type = lex_client.get_slot_type(name='instance_identifiers', version='$LATEST')
	    print response_get_slot_type
	    slot_values_present = []
	    for evals in response_get_slot_type[enumerationValues]:
	        slot_values_present.append(evals['value'])
	        print slot_values_present
        
        user_input = intent_request['currentIntent']['inputTranscript'].split()
        
	    
	    response_put_slot_type = lex_client.put_slot_type(name='instance_identifiers',enumerationValues=[{'value': 'ekta'}],checksum='0379e74f-1cbe-4a3a-8fd0-efeba73c608f')
	    instance_identifier = 'none' '''
	#print (type(instance_action))
	#print (type(instance_identifier))
	#response_all_instances = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name','Values': ['*'instance_identifier'*']}])
	#print (response_all_instances)
	response_describe = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name','Values': ['*'+instance_identifier+'*']}])
	print response_describe
	words_show = ['show','list']
	words_start = ['start'] 
	words_stop = ['stop']
	instance_ids = []
	instance_names = []
	if instance_action in words_show:
	    for i in range(0, len(response_describe['Reservations'])):
	       for j in range(0, len(response_describe['Reservations']['i']['Instances'])):
	           for k in range(0, len(response_describe['Reservations']['i']['Instances']['j']['Tags'])):
	               if(response_describe['Reservations']['i']['Instances']['j']['Tags']['k']['Key'] == 'Name'):
	                   instance_names.append(response_describe['Reservations']['i']['Instances']['j']['Tags']['k']['Value'])
	                   break
	    str1 = ''.join(instance_names)
	    print str1
    	return close(
    		'Fulfilled',
    		{
    			'contentType': 'PlainText',
    			'content': 'These are the instances:-'
            }
        )
	
	if instance_action in words_start:
	    #response_action = ec2_client.start_instances(Filters=[{'Name': 'tag:Name','Values': ['*'instance_identifier'*']}])
	    print('startAction')
	if instance_action in words_stop:
	    #response_action = ec2_client.stop_instances(Filters=[{'Name': 'tag:Name','Values': ['*'instance_identifier'*']}])
	    print('stopAction')
	
	return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'The instance you have requested has been started.'+instance_identifier+instance_action
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
	
	if intent_name == 'action_instances':
		return action_instance(intent_request)
	
	else :
		return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'The request which you are looking for does not support with the current release '
					 
                      
        }
    )


# --- Main handler ---

def lambda_handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
	os.environ['TZ'] = 'America/New_York'
	time.tzset()
	logger.debug('event.bot.name={}'.format(event['bot']['name']))
	return dispatch(event)