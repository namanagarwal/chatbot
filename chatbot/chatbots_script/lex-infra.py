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
#ec21 = boto3.client('ec2')

#instances_new = ['i-0694538dcecccd286', 'i-0750818866f582046', 'i-08b13efc08deeab53']

# List of all the instances in the account

def list_all_instances(intent_request):
	instances = ec2.instances.filter(
	Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
	insts = ""
	for instance in instances:
		if instance.tags:
			for tag in instance.tags:
				if tag['Key'] == 'Name':
					insts = insts+" \t "+ "\n" +tag['Value']
		#if 'Name' in instance.tags:
			#insts = insts+" "+instance.tags['Name']
		print (instance.id, instance.instance_type, instance.tags)
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Here is the following List of All the Instances.'+insts
        }
    )

	

# List of all the running instances

def list_all_run_instances(intent_request):
	instances = ec2.instances.filter(
	Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
	insts = ""
	for instance in instances:
		if instance.tags:
				for tag in instance.tags:
					if tag['Key'] == 'Name':
						insts = insts+" \t "+ "\n" +tag['Value']
			#if 'Name' in instance.tags:
				#insts = insts+" "+instance.tags['Name']
		print (instance.id, instance.instance_type, instance.state)
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Here is the following list of All the Running Instances.' + insts
        }
    )

	
# List of all the stopped instances
	
def list_all_stop_instances(intent_request):
	instances = ec2.instances.filter(
	Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
	insts = ""
	for instance in instances:
		if instance.tags:
				for tag in instance.tags:
					if tag['Key'] == 'Name':
						insts = insts+" \t "+ "\n" +tag['Value']
			#if 'Name' in instance.tags:
				#insts = insts+" "+instance.tags['Name']		
		print (instance.id, instance.instance_type, instance.state)
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Here is the following List of All the Stopped Instances.' + insts
        }
    )
	
	
# Stop an instance
	
def stop_instance(intent_request):
	instances_new = ['i-0694538dcecccd286', 'i-0750818866f582046', 'i-08b13efc08deeab53']
	#ec2.instances.filter(InstanceIds=instances_new).stop()
	ec2.stop_instances(InstanceIds=instances_new)
	for instance in instances:
		print (instance.id, instance.instance_type, instance.state)
	return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'The instance you have requested has been stopped or shut down.'
        }
    )
	

	
	
	
# Start an instance
	
def start_instance(intent_request):
	instances_new = ['i-0694538dcecccd286', 'i-0750818866f582046', 'i-08b13efc08deeab53']
	ec2.start_instances(InstanceIds=instances_new)
	print str(instances)
	return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'The instance you have requested has been started.'
        }
    )
	
	
# Create an instance
	
def create_instance(intent_request):
	ec2.create_instances(ImageId='ami-e659c7f0', MinCount=1, MaxCount=2)
	print str(instances)
	return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Instances have been created as per your request.'
        }
    )
	
# Terminate an instance
	
def terminate_instance(intent_request):
	ids = ['i-0f8393951d5142f9c','i-0b16d4021bc3c07f9']
	ec2.instances.filter(InstanceIds=ids).terminate()
	print str(instances)
	return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Instances have been terminated as per your request.'
        }
    )
		
#ec2.instances.filter(InstanceIds=ids).terminate()
	
	
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
	# Dispatch to your bot's intent handlers
	if intent_name == 'list_all_instances':
		return list_all_instances(intent_request)
	elif intent_name == 'list_all_run_instances':
		return list_all_run_instances(intent_request)
	elif intent_name == 'list_all_stop_instances':
		return list_all_stop_instances(intent_request)
	elif intent_name == 'create_instance':
		return create_instance(intent_request)
	elif intent_name == 'stop_instance':
		return stop_instance(intent_request)
	elif intent_name == 'start_instance':
		return start_instance(intent_request)
	elif intent_name == 'terminate_instance':
		return terminate_instance(intent_request)
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