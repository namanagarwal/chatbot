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
ambariUser = 'admin'
ambariPass = 'admin'
	
def services_list(intent_request):
	
	instance_identifier = intent_request['currentIntent']['slots']['instance_identifier']
	#which_stacks = intent_request['currentIntent']['slots']['which_stack']
	response_describe = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name','Values': ['*'+instance_identifier+'*']}])
	
	print response_describe
	words_show = ['show','list']
	statck_list_dev = ['dev']
	stack_list_int = ['integration','int','nonprod']
	stack_list_prod = ['prod','prodstage']
	words_start = ['start'] 
	words_stop = ['stop']
	instance_ids = []
	instance_id = []
	instance_names = []
	instance_states = []
	instance_states_1 = []
	total_instances = 0
	
	for i in range(0, len(response_describe['Reservations'])):
	   for j in range(0, len(response_describe['Reservations'][i]['Instances'])):
	       instance_ids.append(response_describe['Reservations'][i]['Instances'][j]['InstanceId'])
	
	for i in range(0, len(response_describe['Reservations'])):
	   for j in range(0, len(response_describe['Reservations'][i]['Instances'])):
	       for k in range(0, len(response_describe['Reservations'][i]['Instances'][j]['Tags'])):
	           if('Ambari'in (response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Value']) or ('ambari'in (response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Value'] ))):
	               instance_id = response_describe['Reservations'][i]['Instances'][j]['InstanceId']
                   #print instance_id
                   str2 = instance_id
                   #print instance_id
                   #instance_names.append(response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Value'])
                   #total_instances +=1
                   #break
	#str1 = ' , '+'\n'.join(instance_names)
	#print 'wow'
	print instance_id
	print 'Not Now :('
	print 'There are a total of  '+str(total_instances)+'  Instances and they are as follows:-'+'\n'+str2
	check_service_list(instance_id)
    #return check_service_list(instance_id)
	return elicit(
    		'Fulfilled',
    		{
    			'contentType': 'PlainText',
    			'content': 'Working Now'
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
	
	if intent_name == 'services_check':
		return services_list(intent_request)
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

def check_service_list(ip):
	try:
		print("getting service list")
		response_instance = client_ec2.describe_instances( InstanceIds = [ip])
		print("DNS: " + response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName'])
		base_url = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8444/api/v1/clusters'
		r = requests.get(base_url, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
		cluster_name = r.json()['items'][0]['Clusters']['cluster_name']
		print ("cluster name")
		print (cluster_name)
		base_url_services = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8444/api/v1/clusters/'+cluster_name+'/services'
		r_services = requests.get(base_url_services, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
		print(r_services.json())
		service_list = []
		for i in range(0,len(r_services.json()['items'])):
			service_list.append(r_services.json()['items'][i]['ServiceInfo']['service_name'])
		print (service_list)
		
	except Exception as e:
		print(e)
	
	return service_list