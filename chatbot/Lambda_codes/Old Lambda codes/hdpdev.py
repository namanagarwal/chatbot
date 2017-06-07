import datetime
#from datetime import datetime
import urllib
import urllib2
import json
import boto3
import pytz
import requests
import time
import os
import logging
import re
from botocore.exceptions import ClientError 
from requests.auth import HTTPBasicAuth
from pytz import timezone
from urllib2 import Request, urlopen, URLError, HTTPError
client_ec2 = boto3.client('ec2')
client_cfn = boto3.client('cloudformation')
client_ats = boto3.client('autoscaling')
#ambariPass = os.environ['ambariPassword']
client_db = boto3.client('dynamodb')
#print('This is My Ambari Password:-' + ambariPass)
ambariUser = 'admin'
ambariPass = 'admin'
print('This is My Ambari Password:-' + ambariPass)
HOOK_URL = "https://hooks.slack.com/services/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"


def lambda_handler(event, context):

	dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
	table = dynamodb.Table('ResourceTable')

	from base64 import b64decode
	from urllib2 import Request, urlopen, URLError, HTTPError

	
	print('Starting')
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)
	response_scan = client_db.scan(TableName='ResourceTable')
	print(response_scan)
	now = datetime.datetime.now(timezone('US/Eastern'))
	print('current time EST is:-')
	print(now)
	#day_no = datetime.datetime.today().weekday()
	day_no = now.weekday()
	print('day_no is '+ str(day_no))
	count_stacks = response_scan['Count']
	for i in range(0,count_stacks):
		instanceList = []
		stack_name = response_scan['Items'][i]['stackName']	
		print(stack_name)
		if 'aws-hdp-platform-lmb-nonprod-dev' in stack_name['S']:
			instanceList = response_scan['Items'][i]['instanceIds']['SS']
			print(instanceList)
			startTimeString = response_scan['Items'][i]['days']['M'][str(day_no)]['M']['start']['S']
			startHour = int(startTimeString.split(':')[0])
			startMin = int(startTimeString.split(':')[1])
			stopTimeString = response_scan['Items'][i]['days']['M'][str(day_no)]['M']['stop']['S']
			stopHour = int(stopTimeString.split(':')[0])
			stopMin = int(stopTimeString.split(':')[1])
			startTime = int(startHour)
			stopTime = int(stopHour)
			print('Start Hour is ')
			print(startHour)
			print('Start Min is')
			print(startMin)
			print('Stop Hour is')
			print(stopHour)
			print('Stop Min is')
			print(stopMin)
			asgList = response_scan['Items'][i]['autoScalingGroups']['SS']
			print(asgList)
			try:
				response_instance = client_ec2.describe_instances(InstanceIds = instanceList)
				#print (response_instance)
			except ClientError as e:
				logger.error("Received error: %s", e, exc_info=True)
				if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
					print (e)
					print('error has beeen printed')
					missing_instances = re.findall(r"'(.*?)'", e.response['Error']['Message'])[0].replace("'", "").split(", ")
					instanceList = list(set(instanceList) - set(missing_instances))
					print(instanceList)
					response_instance = client_ec2.describe_instances(InstanceIds = instanceList)
			for j in range(0,len(instanceList)):
				tag_length = len(response_instance['Reservations'][j]['Instances'][0]['Tags'])
				print(tag_length)
				for k in range (0,tag_length):
					if 'Ambari' in response_instance['Reservations'][j]['Instances'][0]['Tags'][k]['Value']:
						ambariIp = response_instance['Reservations'][j]['Instances'][0]['InstanceId']
						#check if its a weekend.
						#print("Its a weekday")
			print('ambariIp is')
			print(ambariIp)
			print(now.hour)
			print(now.minute)
			if int(startTime) > int(stopTime):
				print('Reverse')
				if int(startTime) <= now.hour:
					print("Its Within hour limit to start the instances")
					if (now.hour ==  (int(stopTime) - 1) and int(stopHour) != 24):
						if (now.minute >= int(stopMin)):
							response_get = table.get_item(Key={'stackName': stack_name['S'] })
							flagIA = response_get['Item']['instanceAlertFlag']
							if flagIA != 1:
								print("sending stop alert")
								send_alert(stack_name,'Stop',stopTimeString)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 1},ReturnValues="UPDATED_NEW")
					elif (now.hour ==  int(stopHour)):
						if (now.minute < int(stopMin)):
							response_get = table.get_item(Key={'stackName': stack_name['S'] })
							flagIA = response_get['Item']['instanceAlertFlag']
							if flagIA != 1:
								print("sending stop alert")
								send_alert(stack_name,'Stop',stopTimeString)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 1},ReturnValues="UPDATED_NEW")
					if int(startMin) <= now.minute :
						print("Its Within Minutes limit to start the instances")
						for j in range(0,len(response_instance))::
							if response_instance['Reservations'][j]['Instances'][0]['State']['Name'] != 'running':
								try:
									client_ec2.start_instances( InstanceIds = instanceList)
									response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 0},ReturnValues="UPDATED_NEW")
								except ClientError as e:
									logger.error("Received error: %s", e, exc_info=True)
									if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
										print (e)
										print('error has beeen printed')
										missing_instances = re.findall(r"'(.*?)'", e.response['Error']['Message'])[0].replace("'", "").split(", ")
										instanceList = list(set(instanceList) - set(missing_instances))
										print(instanceList)
										client_ec2.start_instances( InstanceIds = instanceList)
										response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 0},ReturnValues="UPDATED_NEW")
								print("waiting for 120 seconds so that all the instances are up and running properly")
								time.sleep(120)
								print("Starting services now")
								services_on(ambariIp)
								cluster_service_list = check_service_list(ambariIp)
								s_dict = check_service_state(cluster_service_list,ambariIp)
								flag = 0
								while (flag == 0):
									len_dict = len(s_dict)
									print("number of services: "+ str(len_dict))
									count = 0
									for key,value in s_dict.iteritems():
										count = count + 1
										if value != 'STARTED':
											print(key +' is still not started successfully')
											time.sleep(10)
											services_on(ambariIp)
											s_dict = check_service_state(cluster_service_list,ambariIp)
										if count == len_dict:
											print("changed flag status to 1")
											flag = 1
								print("Started All services")	
							else:
								print('It is already running')	
				elif int(stopTime) <= now.hour < int(startTime):
					print("Its Within hour limit to stop the instances")
					if (now.hour ==  (int(startHour) - 1) and int(startHour) != 24):
						if (now.minute >= int(startMin)):
							response_get = table.get_item(Key={'stackName': stack_name['S'] })
							flagIA = response_get['Item']['instanceAlertFlag']
							if flagIA != 1:
								print("sending start alert")
								send_alert(stack_name,'Start',startTimeString)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 1},ReturnValues="UPDATED_NEW")
					elif (now.hour ==  int(startHour)):
						if (now.minute < int(stopMin)):
							response_get = table.get_item(Key={'stackName': stack_name['S'] })
							flagIA = response_get['Item']['instanceAlertFlag']
							if flagIA != 1:
								print("sending start alert")
								send_alert(stack_name,'Start',startTimeString)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 1},ReturnValues="UPDATED_NEW")
					for j in range(0,len(response_instance)):
						if (response_instance['Reservations'][j]['Instances'][0]['State']['Name'] == 'stopped' or response_instance['Reservations'][j]['Instances'][0]['State']['Name'] == 'stopping'):
							print('Instances Already Stopped')
						else:
							print("Not Within Time Limit")
							services_off(ambariIp)
							print("Switching OFF the services")
							cluster_service_list = check_service_list(ambariIp)
							s_dict = check_service_state(cluster_service_list,ambariIp)
							flag = 0
							while (flag == 0):
								len_dict = len(s_dict)
								print("number of services: "+ str(len_dict))
								count = 0
								for key,value in s_dict.iteritems():
									count = count + 1
									print(str(count) + 'service stopped:-' + key )
									if value != 'INSTALLED' and value != 'UNKNOWN':
										print(key +' is still not stopped successfully')
										time.sleep(10)
										s_dict.clear()
										s_dict = check_service_state(cluster_service_list,ambariIp)
										time.sleep(5)
									if count == len_dict:
										print("changed flag status to 1")
										flag = 1
							print("Switched off services")
							for group in asgList:
								client_ats.suspend_processes(AutoScalingGroupName = group ,ScalingProcesses=['HealthCheck','ReplaceUnhealthy'])
								print("suspended group " + group)
							try:
								client_ec2.stop_instances( InstanceIds = instanceList)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 0},ReturnValues="UPDATED_NEW")
							except ClientError as e:
								logger.error("Received error: %s", e, exc_info=True)
								if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
									print (e)
									print('error has beeen printed')
									missing_instances = re.findall(r"'(.*?)'", e.response['Error']['Message'])[0].replace("'", "").split(", ")
									instanceList = list(set(instanceList) - set(missing_instances))
									print(instanceList)
									client_ec2.stop_instances( InstanceIds = instanceList)
									response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 0},ReturnValues="UPDATED_NEW")
							print("stopped instances")
			else:
				if int(startTime) <= now.hour < int(stopTime):
					print("Its Within hour limit to start the instances")
					if (now.hour ==  (int(stopHour) - 1)  and int(stopHour) != 24):
						if ( int(stopMin) <= int(now.minute)):
							response_get = table.get_item(Key={'stackName': stack_name['S'] })
							flagIA = response_get['Item']['instanceAlertFlag']
							if flagIA != 1:
								print("sending stop alert")
								send_alert(stack_name,'Stop',stopTimeString)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 1},ReturnValues="UPDATED_NEW")
					elif ( now.hour ==  int(stopHour)):
						if ( int(now.minute) < int(stopMin)):
							response_get = table.get_item(Key={'stackName': stack_name['S'] })
							flagIA = response_get['Item']['instanceAlertFlag']
							if flagIA != 1:
								print("sending stop alert")
								send_alert(stack_name,'Stop',stopTimeString)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 1},ReturnValues="UPDATED_NEW")
					if startMin <= now.minute :
						print("Its Within Minutes limit")
						for j in range(0,len(response_instance)):
							if response_instance['Reservations'][j]['Instances'][0]['State']['Name'] != 'running':
								try:
									client_ec2.start_instances( InstanceIds = instanceList)
									response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 0},ReturnValues="UPDATED_NEW")
								except ClientError as e:
									logger.error("Received error: %s", e, exc_info=True)
									if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
										print (e)
										print('error has beeen printed')
										missing_instances = re.findall(r"'(.*?)'", e.response['Error']['Message'])[0].replace("'", "").split(", ")
										instanceList = list(set(instanceList) - set(missing_instances))
										print(instanceList)
										client_ec2.start_instances( InstanceIds = instanceList)
										response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 0},ReturnValues="UPDATED_NEW")
								print("waiting for 120 seconds so that all the instances are up and running properly")
								time.sleep(120)
								print("Starting services now")
								services_on(ambariIp)
								cluster_service_list = check_service_list(ambariIp)
								s_dict = check_service_state(cluster_service_list,ambariIp)
								flag = 0
								while (flag == 0):
									len_dict = len(s_dict)
									print("number of services: "+ str(len_dict))
									count = 0
									for key,value in s_dict.iteritems():
										count = count + 1
										if value != 'STARTED':
											print(key +' is still not started successfully')
											time.sleep(10)
											services_on(ambariIp)
											s_dict = check_service_state(cluster_service_list,ambariIp)
										if count == len_dict:
											print("changed flag status to 1")
											flag = 1
								print("Started All services")	
							else:
								print('It is already running')	
				else:
					if (now.hour ==  (int(startHour) - 1) and int(startHour) != 24):
						if (now.minute >= int(startMin)):
							response_get = table.get_item(Key={'stackName': stack_name['S'] })
							flagIA = response_get['Item']['instanceAlertFlag']
							if flagIA != 1:
								print("sending start alert")
								send_alert(stack_name,'Start',startTimeString)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 1},ReturnValues="UPDATED_NEW")
					elif (now.hour ==  int(startHour)):
						if (now.minute < int(stopMin)):
							response_get = table.get_item(Key={'stackName': stack_name['S'] })
							flagIA = response_get['Item']['instanceAlertFlag']
							if flagIA != 1:
								print("sending start alert")
								send_alert(stack_name,'Start',startTimeString)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 1},ReturnValues="UPDATED_NEW")
					for j in range(0,len(response_instance)):
						if (response_instance['Reservations'][j]['Instances'][0]['State']['Name'] == 'stopped' or response_instance['Reservations'][j]['Instances'][0]['State']['Name'] == 'stopping'):
							print('Instances Already Stopped')
						else:
							print("Not Within Time Limit")
							services_off(ambariIp)
							print("Switching OFF the services")
							cluster_service_list = check_service_list(ambariIp)
							s_dict = check_service_state(cluster_service_list,ambariIp)
							flag = 0
							while (flag == 0):
								len_dict = len(s_dict)
								print("number of services: "+ str(len_dict))
								count = 0
								for key,value in s_dict.iteritems():
									count = count + 1
									#print(str(count) + 'service stopped:-' + key )
									if (value != 'INSTALLED' and value != 'UNKNOWN'):
										print(key +' is still not stopped successfully')
										time.sleep(10)
										s_dict.clear()
										s_dict = check_service_state(cluster_service_list,ambariIp)
										time.sleep(5)
									if count == len_dict:
										print("changed flag status to 1")
										flag = 1
							print("Switched off services")
							for group in asgList:
								client_ats.suspend_processes(AutoScalingGroupName = group ,ScalingProcesses=['HealthCheck','ReplaceUnhealthy'])
								print("suspended group " + group)
							try:
								client_ec2.stop_instances( InstanceIds = instanceList)
								response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 0},ReturnValues="UPDATED_NEW")
							except ClientError as e:
								logger.error("Received error: %s", e, exc_info=True)
								if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
									print (e)
									print('error has beeen printed')
									missing_instances = re.findall(r"'(.*?)'", e.response['Error']['Message'])[0].replace("'", "").split(", ")
									instanceList = list(set(instanceList) - set(missing_instances))
									print(instanceList)
									client_ec2.stop_instances( InstanceIds = instanceList)
									response = table.update_item(Key={'stackName': stack_name['S'] },  UpdateExpression="set instanceAlertFlag = :r",ExpressionAttributeValues={ ':r' : 0},ReturnValues="UPDATED_NEW")
							print("stopped instances")
			break
def services_on(ip):
    try:
		
		response_instance = client_ec2.describe_instances( InstanceIds = [ip])
		print("DNS: " + response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName'])
		base_url = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8444/api/v1/clusters'
		r = requests.get(base_url, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
		cluster_name = r.json()['items'][0]['Clusters']['cluster_name']
		print ("cluster name")
		print (cluster_name)
		
		#Start All Services
		status = base_url+'/'+cluster_name+'/services'
		startdata = {"RequestInfo":{"context":"_PARSE_.START.ALL_SERVICES","operation_level":{"level":"CLUSTER","cluster_name":"Sandbox"}},"Body":{"ServiceInfo":{"state":"STARTED"}}}
		headers = {"X-Requested-By": "ambari"}
		response = requests.put(status, auth=HTTPBasicAuth(ambariUser, ambariPass), data=json.dumps(startdata), headers=headers, verify=False)
		print("Start Services Executed")
		
    except Exception as e:
		print(e)
		time.sleep(10)
		services_on(ip)

def services_off(ip):
    try:
		response_instance = client_ec2.describe_instances( InstanceIds = [ip])
		print("DNS: " + response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName'])
		base_url = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8444/api/v1/clusters'
		r = requests.get(base_url, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
		cluster_name = r.json()['items'][0]['Clusters']['cluster_name']
		print ("cluster name")
		print (cluster_name)
		
		#Stop All Services
		status = base_url+'/'+cluster_name+'/services'
		stopdata = {"RequestInfo":{"context":"_PARSE_.STOP.ALL_SERVICES","operation_level":{"level":"CLUSTER","cluster_name":"Sandbox"}},"Body":{"ServiceInfo":{"state":"INSTALLED"}}}
		headers = {"X-Requested-By": "ambari"}
		response = requests.put(status, auth=HTTPBasicAuth(ambariUser, ambariPass), data=json.dumps(stopdata), headers=headers, verify=False)
		print("Stop Services Executed")
		#time.sleep(50)
		#while requests.get(status, auth=HTTPBasicAuth('admin', 'admin'), verify=False).json()['ServiceInfo']['state'] != 'INSTALLED':
        #            print "Waiting for HDFS services to stop..."
        #            print requests.get(hdfs_status, auth=HTTPBasicAuth('admin', 'admin'), verify=False).json()['ServiceInfo']['state']
        #           time.sleep(5)
    except Exception as e:
		print(e)
		time.sleep(10)
		services_off(ip)

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

def check_service_state(s_list,ip):
	try:
		response_instance = client_ec2.describe_instances( InstanceIds = [ip])
		print("DNS: " + response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName'])
		base_url = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8444/api/v1/clusters'
		r = requests.get(base_url, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
		cluster_name = r.json()['items'][0]['Clusters']['cluster_name']
		
		print("checking state")
		service_dict = {}
		#GET api/v1/clusters/c1/services/HDFS?fields=ServiceInfo/state
		for service in s_list:
			print('turning Off maintenance mode ' + service)
			maintenanceURL = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8444/api/v1/clusters/'+cluster_name+'/services/'+service
			stopdata = {"RequestInfo":{"context":"Turn Off Maintenance Mode"},"Body":{"ServiceInfo":{"maintenance_state":"OFF"}}}
			headers = {"X-Requested-By": "ambari"}
			response = requests.put(maintenanceURL, auth=HTTPBasicAuth(ambariUser, ambariPass), data=json.dumps(stopdata), headers=headers, verify=False)
			print('maintenance resposne is')
			print(response)
			#curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Remove Falcon from maintenance mode"}, "Body": {"ServiceInfo": {"maintenance_state": "OFF"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/FALCON
			#print('Service check begins')
			base_url_state = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8444/api/v1/clusters/'+cluster_name+'/services/'+service+'?fields=ServiceInfo/state'
			print(base_url_state)
			r_state = requests.get(base_url_state, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
			print(r_state)
			print(r_state.json())
			state_of_service = r_state.json()['ServiceInfo']['state']
			print(service +' = '+ state_of_service)
			service_dict[service] = state_of_service
		
		return service_dict
	
	except Exception as e:
		print(e)
		
def send_alert(stack,state,timing):
	d = datetime.datetime.strptime(timing, "%H:%M")
	timing = d.strftime("%I:%M %p")
	if(state == 'Start'):
		slack_message = {
			"text": stack['S'] + "will start at " + str(timing) + " EST." ,
			"channel" : "#instance_alerts",
			"username" : stack['S']
		}
	elif (state == 'Stop'):
		slack_message = {
			"text": stack['S'] + "will stop at " + str(timing) + " EST.",
			"channel" : "#instance_alerts",
			"username" : stack['S']
		}
	
	req = Request(HOOK_URL, json.dumps(slack_message))
	try:
		response = urlopen(req)
		response.read()
		logger.info("Message posted to %s", slack_message['channel'])
	except HTTPError as e:
		logger.error("Request failed: %d %s", e.code, e.reason)
	except URLError as e:
		logger.error("Server connection failed: %s", e.reason)