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

	
def Status_list_machines(intent_request):
	#Status_list_machines = intent_request['currentIntent']['slots']['Status_list_machiness']
	instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
	which_stacks = intent_request['currentIntent']['slots']['which_stack']
	#print (type(Status_list_machines))
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
	instance_states = []
	instance_states_1 = []
	total_instances = 0
	
	for i in range(0, len(response_describe['Reservations'])):
	   for j in range(0, len(response_describe['Reservations'][i]['Instances'])):
	       instance_ids.append(response_describe['Reservations'][i]['Instances'][j]['InstanceId'])
	       
	for i in range(0, len(response_describe['Reservations'])):
	   for j in range(0, len(response_describe['Reservations'][i]['Instances'])):
	       for k in range(0, len(response_describe['Reservations'][i]['Instances'][j]['State'])):
		       instance_states_1.append(response_describe['Reservations'][i]['Instances'][j]['State'][k]['Name'])
	           
    
	
	for i in range(0, len(response_describe['Reservations'])):
	   for j in range(0, len(response_describe['Reservations'][i]['Instances'])):
	       for k in range(0, len(response_describe['Reservations'][i]['Instances'][j]['Tags'])):
	           if(response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Key'] == 'Name'):
	               instance_names.append(response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Value'])
	               instance_states.append(response_describe['Reservations'][i]['Instances'][j]['State'][k]['Name'])
	               #print 'Just for sample testing'
	               #print instance_states
	               total_instances +=1
	               break
	str1 = ' , '+'\n'.join(instance_names)
	print str1
	output_message = 'There are a total of  '+str(total_instances)+'  Instances and they are as follows:-'+'\n'+str1
    
	return elicit(
    		'Fulfilled',
    		{
    			'contentType': 'PlainText',
    			'content': output_message
            }
            )
	
		
# Greetings

def greetings(intent_request):
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Hi, I am LabRat, a Chatbot. I can help you with DataLake related queries.'
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
	
	if intent_name == 'Status_list_machines':
		return Status_list_machines(intent_request)
	elif intent_name == 'greetings':
	    return greetings(intent_request)
	
	else :
		return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Sorry!!  The request which you are looking for does not support with the current release '
					 
                      
        }
    )


# --- Main handler ---

def lambda_handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
	os.environ['TZ'] = 'America/New_York'
	time.tzset()
	logger.debug('event.bot.name={}'.format(event['bot']['name']))
	return dispatch(event)