import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
import collections
import re

region = 'us-east-1'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ec2 = boto3.resource('ec2', region_name=region)
ec2_client = boto3.client('ec2')

def list_instance_untagged(intent_request):
	instances = ec2.instances.filter(
	Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
	insts = ""
	for instance in instances:
	    present_instance = 0
	    if len(instance.tags) > 0:
	        for tag in instance.tags:
	            if tag['Key'].lower() == 'owner':
	                present_instance = 1
            if present_instance == 0:
                for tag in instance.tags:
    		        if tag['Key'] == 'Name':
    				    insts = insts + " \t "+ "\n" +tag['Value'] + ","
    	
    	        
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'These are the untagged instances :- ' + '\n' +insts
        }
    )

# List of all the tagged instances in the account

def list_instance_tagged(intent_request):
	instances = ec2.instances.filter(
	Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
	insts = ""
	for instance in instances:
		if instance.tags:
			for tag in instance.tags:
				if tag['Key'] == 'Name':
					insts = insts+" \t "+ "\n" +tag['Value'] + ","
		#if 'Name' in instance.tags:
			#insts = insts+" "+instance.tags['Name']
		#print (instance.id, instance.instance_type, instance.tags)
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Here is the following List of All the Instances.'+insts
        }
    )
	
# List of all the instances in the Account
def list_all_instances(intent_request):
	instances = ec2.instances.filter(
	Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
	insts = ""
	for instance in instances:
		if instance.tags:
				for tag in instance.tags:
					if tag['Key'] == 'Name':
						insts = insts+" \t "+ "\n" +tag['Value']  + ","
		print (instance.id, instance.instance_type, instance.state)
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'There are a total of these many instances in your AWS Account as of now. Do you want me to list them out?' + len(response[instance])
        }
    )

def list_all_named(intent_request):
	instances = ec2.instances.filter(
	Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
	insts = ""
	for instance in instances:
		if instance.tags:
				for tag in instance.tags:
					if tag['Key'] == 'Name':
						insts = insts+" \t "+ "\n" +tag['Value']  + ","
		print (instance.id, instance.instance_type, instance.state)
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Here is the following List of All the Stopped Instances.' + insts
        }
    )
		
	
	
# List of all the running instances

def list_all_run_instances(intent_request):
	instances = ec2.instances.filter(
	Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
	insts = ""
	counter = len(instances)
	for instance in instances:
	    #counter = counter + 1
	    #println("All Good")
		if instance.tags:
				for tag in instance.tags:
					
					if tag['Key'] == 'Name':
						insts = insts+" \t "+ "\n" +tag['Value']  + ","
			#if 'Name' in instance.tags:
				#insts = insts+" "+instance.tags['Name']
		print (instance.id, instance.instance_type, instance.state)
	print (counter)
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'There are a total of running instances as of now.' + insts
        }
    )

	
# List of all the stopped instances
	
def list_all_stop_instances(intent_request):
	instances = ec2.instances.filter(
	Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
	insts = ""
	counter = 0
	for instance in instances:
		if instance.tags:
				for tag in instance.tags:
					counter = counter+1
					if tag['Key'] == 'Name':
						insts = insts+" \t "+ "\n" +tag['Value'] + ","					
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
	instances_new = ['i-03950f9877c93e440']#, 'i-0750818866f582046', 'i-08b13efc08deeab53']
	response_stop = ec2_client.stop_instances(InstanceIds=instances_new)
	print response_stop
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'The instance you have requested has been stopped.'+ str(instances_new)
        }
    )
	
	
	
	
# Start an instance
	
def start_instance(intent_request):
	#instances_new = ['i-03950f9877c93e440']#, 'i-0750818866f582046', 'i-08b13efc08deeab53']
	#response_start = ec2_client.start_instances(InstanceIds=instances_new)
	#print response_start
	#return elicit(
	#	'Fulfilled',
	#	{
	#		'contentType': 'PlainText',
	#		'content': 'The instance you have requested has been started.'+ str(instances_new)
    #    }
    #)
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Which all instances you want to start?'
        }
    )
	
# Define which all instacnes you want to perform 

def which_instance_start(intent_request):
	
	instance = intent_request['currentIntent']['slots']['instance_tag_name']
	print ('HI')
	print (instance)
	
	instances_new = ['i-03950f9877c93e440']
	response_start = ec2_client.start_instances(InstanceIds=instances_new)
	print response_start
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'The instance you have requested has been started.'+ str(instances_new)
        }
    )
	
	
	
# Create an instance
	
def create_instance(intent_request):
	ec2.create_instances(ImageId='ami-e659c7f0', MinCount=1, MaxCount=2)
	print str(instances)
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Instances have been created as per your request.'
        }
    )
	
# Terminate an instance
	
def terminate_instance(intent_request):
	ids = ['i-01b6ffa8a9289ef6e','i-08dd45f09c0a4c71a']
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

# Greetings

def greetings(intent_request):
	return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Hello!! My name is LabRat,  How can I help you today?'
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
	# Dispatch to your bot's intent handlers
	if intent_name == 'list_all_instances':
		return list_all_instances(intent_request)
	elif intent_name == 'list_all_run_instances':
		return list_all_run_instances(intent_request)
	elif intent_name == 'list_all_stop_instances':
		return list_all_stop_instances(intent_request)
	elif intent_name == 'create_instance':
		return create_instance(intent_request)
	elif intent_name == 'Stop_instance':
		return stop_instance(intent_request)
	elif intent_name == 'start_instance':
		return start_instance(intent_request)
	elif intent_name == 'terminate_instance':
		return terminate_instance(intent_request)
	elif intent_name == 'greetings':
		return greetings(intent_request)
	elif intent_name == 'list_instance_untagged':
		return list_instance_untagged(intent_request)
	elif intent_name == 'list_instance_tagged':
		return list_instance_tagged(intent_request)
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