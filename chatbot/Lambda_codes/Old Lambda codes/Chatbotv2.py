import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
import re
import pymssql

region = 'us-east-1'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ec2 = boto3.resource('ec2', region_name=region)
ec2_client = boto3.client('ec2')
lex_client = boto3.client('lex-models')
cloudwatch = boto3.client('cloudwatch')
ambariUser = admin
ambariPass = admin


server = 'chatbottestdb.cniw8p6tx7sx.us-east-1.rds.amazonaws.com'
user = 'shubhamkackar'
password = 'arsenal1994'
'''
with open('AWS_Pricing.csv', 'rb') as price_chart:
    reader = csv.reader(price_chart, delimiter=',')
    price_chart_list = list(reader)
    total_rows = len(price_chart_list)
'''

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
	total_instances = 0
	
	for i in range(0, len(response_describe['Reservations'])):
	   for j in range(0, len(response_describe['Reservations'][i]['Instances'])):
	       instance_ids.append(response_describe['Reservations'][i]['Instances'][j]['InstanceId'])
    
	
	if instance_action in words_show:
	    for i in range(0, len(response_describe['Reservations'])):
	       for j in range(0, len(response_describe['Reservations'][i]['Instances'])):
	           for k in range(0, len(response_describe['Reservations'][i]['Instances'][j]['Tags'])):
	               if(response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Key'] == 'Name'):
	                   instance_names.append(response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Value'])
	                   total_instances +=1
	                   break
	    str1 = ' , \n'.join(instance_names)
	    print str1
	    output_message = 'There are a total of  '+str(total_instances)+'  Instances and they are as follows:-'+'\n'+str1
    
	if instance_action in words_start:
	    response_action = ec2_client.start_instances(InstanceIds=instance_ids)
	    print('startAction')
	    output_message = 'The '+str(instance_identifier)+' instance/s you have requested has been '+str(instance_action)+'ed.'
	    
	if instance_action in words_stop:
	    response_action = ec2_client.stop_instances(InstanceIds=instance_ids)
	    print('stopAction')
		#output_message = 'The instance you have requested has been started.'+instance_identifier+instance_action
	    output_message = 'The '+str(instance_identifier)+' instance/s you have requested has been '+str(instance_action)+'ped.'
	#"Observed %s instances running at %s" % (num_instances, timestamp)
	return close(
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
	

# environment Status

def environment_status(intent_request):
    insts = ""
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
    for instance in instances:
        launch_time = instance.launch_time
        current_time = datetime.datetime.now(launch_time.tzinfo)
        lt_delta = current_time - launch_time
        running_time = str(lt_delta)
        lt_Delta_hr = lt_delta.total_seconds()/3600 
        period = 60
        if lt_Delta_hr > 360 and lt_Delta_hr < 1412 :
            period = 300 * int(lt_delta.total_seconds()/1440)
        elif lt_delta.total_seconds()/60 > 1412 :
            period = 3600 * int(lt_delta.total_seconds()/1440)
        results = cloudwatch.get_metric_statistics(Namespace='AWS/EC2', MetricName='CPUUtilization', Dimensions=[{'Name': 'InstanceId', 'Value': instance.id}], StartTime=launch_time, EndTime=current_time, Period=period, Statistics=['Average'])
        length = len(results['Datapoints'])
        if length == 0 : length = 1
        sum_of_avg = 0
        for datapoint in results['Datapoints'] :
            sum_of_avg = sum_of_avg + datapoint['Average']
        average = str(sum_of_avg / length) + '%'
        insts = insts + instance.id + ' , ' + str(instance.launch_time) + ' , ' + running_time + ' , ' + average + ' \n ' 
        print('Instance : ' + instance.id + ', Launch Time : ' + str(instance.launch_time) + ', Running Time : ' + running_time + ', CPU Utilization : ' + average)
    return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Here is the List of instances with  CPU Utilization & Running time.' + insts
        }
    )
    
	
# Pricing Information

def pricing_information(intent_request):
    
    insts = ""
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
    for instance in instances:
        instance_type = instance.instance_type
        launch_time = instance.launch_time
        current_time = datetime.datetime.now(launch_time.tzinfo)
        lt_delta = current_time - launch_time
        running_time_hr = str(lt_delta)

        price = 0.0
        for row_cnt in range(1, total_rows):
            if price_chart_list[row_cnt][0] == region and price_chart_list[row_cnt][1] == instance_type :
                price = price_chart_list[row_cnt][2] * (lt_delta.total_seconds()/3600)
        
        #insts = insts + instance.id + ',' + str(instance.launch_time) + ',' + running_time + ',' + average + '\n' 
        print('Instance : ' + instance.id  + ', Running Time : ' + running_time + ', Instance Type : ' + instance_type + ', Price : ' + str(price))
    return elicit(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Here is the List of instances with  CPU Utilization & Running time.' + insts
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
    elif intent_name == 'greetings':
        return greetings(intent_request)
    elif intent_name == 'environment_status':
        return environment_status(intent_request)
    elif intent_name == 'pricing_information'
	    return pricing_information(intent_request)
	elif intent_name == 'services_check':
        return services_list(intent_request)
    else:
		return close(
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': 'Sorry!!  The request which you are looking for does not support with the current release '
					 
                      
        }
    )

	
# list of services in Ambari
	
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

def check_service_list(ip):
	try:
		print("getting service list")
		response_instance = client_ec2.describe_instances( InstanceIds = [ip])
		print("DNS: " + response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName'])
		base_url = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8080/api/v1/clusters'
		r = requests.get(base_url, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
		cluster_name = r.json()['items'][0]['Clusters']['cluster_name']
		print ("cluster name")
		print (cluster_name)
		base_url_services = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8080/api/v1/clusters/'+cluster_name+'/services'
		r_services = requests.get(base_url_services, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
		print(r_services.json())
		service_list = []
		for i in range(0,len(r_services.json()['items'])):
			service_list.append(r_services.json()['items'][i]['ServiceInfo']['service_name'])
		print (service_list)
		
	except Exception as e:
		print(e)
	
	return service_list

# --- Main handler ---

def lambda_handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
	os.environ['TZ'] = 'America/New_York'
	time.tzset()
	logger.debug('event.bot.name={}'.format(event['bot']['name']))
	#conn = pymssql.connect(server, user, password, "chatbot")
	#cursor = conn.cursor()
	#cursor.execute('SELECT * FROM users')
	#row = cursor.fetchone()
	#while row:
	#	print("ID=%d, Name=%s" % (row[0], row[1]))
	#	row = cursor.fetchone()
	return dispatch(event)