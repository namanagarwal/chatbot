#---------------------- Import packages as per the requirement-----------------------

import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
import re
import requests
#import pymssql
#from datetime import datetime
import urllib
import urllib2
from botocore.exceptions import ClientError 
from requests.auth import HTTPBasicAuth
from urllib2 import Request, urlopen, URLError, HTTPError
import csv

region = 'us-east-1'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ec2 = boto3.resource('ec2', region_name=region)
ec2_client = boto3.client('ec2')
lex_client = boto3.client('lex-models')
cloudwatch = boto3.client('cloudwatch')
ambariUser = "admin"
ambariPass = "admin"


server = 'chatbottestdb.cniw8p6tx7sx.us-east-1.rds.amazonaws.com'
user = 'shubhamkackar'
password = 'arsenal1994'

#----------------------------------AWS Pricing List for CSV -----------------------------------------------

with open('AWS_Pricing.csv', 'rb') as price_chart:
    reader = csv.reader(price_chart, delimiter=',')
    price_chart_list = list(reader)
    total_rows = len(price_chart_list)

#----------------------------------- Greetings--------------------------------------------------------------


def greetings(intent_request):
    return elicit(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hello!! My name is ChatOps, a Chatbot. I can help you with DataLake related queries. \n How can I help you today?'
        }
                  )
            
#--------------------- Start / Stop and List an instance/s in the User Specified environment-----------------
    
def action_instances(intent_request):
    instance_action = intent_request['currentIntent']['slots']['instance_actions']
    instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
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
    response_stack_describe = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name','Values': ['*'+stack_identifier+'*']}])
    print (type(stack_identifier))
    print stack_identifier
    print response_describe
    print response_stack_describe
    words_show = ['show','list','fetch']
    words_start = ['start','bring up','initialise','initialize'] 
    words_stop = ['stop','shut down','Power Off','Power Down','bring down']
    stack_list_dev = ['dev','Dev','Development','DEVELOPMENT','development']
    stack_list_non_prod = ['Non Prod','NON PROD','Non Production','Non-Prod','Non-prod','non prod']
    stack_list_prod_stage = ['Prod-Stage','Production-Stage','production-stage','Prod Stage','prod-stage','Production Stage']
    stack_list_prod = ['prod','PROD','Prod','Production','production']
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
        str1 = ' , \n \t -> '.join(instance_names)
        print str1
        output_message_action_instances = 'There are a total of  '+str(total_instances)+' '+str(instance_identifier)+' Instances in the '+str(stack_identifier)+ ' environment. \n They are as follows:- '+'\n \t -> '+str1
    
    if instance_action in words_start:
        '''for i in range(0, len(response_describe['Reservations'])):
            for j in range(0,len(response_describe['Reservasations'][i]['Instances'])):
                for k in range(0, len(response_describe['Reservations'][i]['Instances'][j]['Tags'])):
                    if(response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Key'] == 'Name'):
                        response_describe = ec2_client.start_instances(InstanceIds=instance_ids)
                        total_instances +=1
                        print('StartAction_individual')
                        break
        '''
        #str1 = ''
        response_action = ec2_client.start_instances(InstanceIds=instance_ids)
        print (response_action)
        #total_instances +=1
        print ('startAction')
        #break
        #str1 = ' , \n \t -> '.join(instance_names)
        #output_message_action_instances = 'There are a total of  '+str(total_instances)+' '+str(instance_identifier)+' Instances in the '+str(stack_identifier)+ ' environment. \n They have been started. \n They are as follows:- '+'\n \t -> '+str1
        output_message_action_instances = '\n The '+str(instance_identifier)+' instance/s you have requested in the '+str(stack_identifier)+ ' environment has been '+str(instance_action)+'ed.'
        
    if instance_action in words_stop:
        response_action = ec2_client.stop_instances(InstanceIds=instance_ids)
        print('stopAction')        
        output_message_action_instances = 'The '+str(instance_identifier)+' instance/s you have requested in the '+str(stack_identifier)  + ' environment has been '+str(instance_action)+'ped.'
    #"Observed %s instances running at %s" % (num_instances, timestamp)
    return close(
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': output_message_action_instances
            }
                 )
    
        
# -------------------------------Instance Utilization wrt Environment Status--------------------------------------

def utilization_statistics(intent_request):
    #instance_action = intent_request['currentIntent']['slots']['instance_actions']
    instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
    
    response_describe = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name','Values': ['*'+instance_identifier+'*']}])
    response_stack_describe = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name','Values': ['*'+stack_identifier+'*']}])
    print (type(stack_identifier))
    print stack_identifier
    print response_describe
    print response_stack_describe
    words_show = ['show','list']
    words_start = ['start'] 
    words_stop = ['stop']
    stack_list_dev = ['dev']
    stack_list_prod = ['prod','PROD','Prod','Production','production']
    instance_ids = []
    instance_names = []
    total_instances = 0
    
    for i in range(0, len(response_describe['Reservations'])):
       for j in range(0, len(response_describe['Reservations'][i]['Instances'])):
           instance_ids.append(response_describe['Reservations'][i]['Instances'][j]['InstanceId'])
    
    
    insts = ""
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
    for instance in instances:
        if (instance.id in instance_ids):
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
            insts = insts +'\n \t --> '+ instance.id + ' , \t ' + str(instance.launch_time) + ' , \t ' + running_time + ' , \t ' + average 
            print('Instance : ' + instance.id + ', Launch Time : ' + str(instance.launch_time) + ', Running Time : ' + running_time + ', CPU Utilization : ' + average)
    message_utilization = 'Here is the List of '+str(instance_identifier) +' instances from the '+str(stack_identifier)+' environment with the Utilization Details :: \n\t\t\t\t INSTANCE ID  \t||\t  LAUNCH TIME \t||\t  RUNNING SINCE \t||\t   CPU UTILIZATION :- ' + insts
    return elicit(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message_utilization
        }
                  )
    

#---------------------------------------- Price and Cost structure of machines based on User Input-----------------------

def pricing_information(intent_request):
    #instance_action = intent_request['currentIntent']['slots']['instance_actions']
    instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
    
    response_describe = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name','Values': ['*'+instance_identifier+'*']}])
    response_stack_describe = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name','Values': ['*'+stack_identifier+'*']}])
    print (type(stack_identifier))
    print stack_identifier
    print response_describe
    print response_stack_describe
    words_show = ['show','list']
    words_start = ['start'] 
    words_stop = ['stop']
    stack_list_dev = ['dev']
    stack_list_prod = ['prod','PROD','Prod','Production','production']
    instance_ids = []
    instance_names = []
    total_instances = 0
    
    for i in range(0, len(response_describe['Reservations'])):
       for j in range(0, len(response_describe['Reservations'][i]['Instances'])):
           instance_ids.append(response_describe['Reservations'][i]['Instances'][j]['InstanceId'])
    
    
    insts = ""
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
    for instance in instances:
        if (instance.id in instance_ids):
            print type(instance)
            instance_type = instance.instance_type
            launch_time = instance.launch_time
            current_time = datetime.datetime.now(launch_time.tzinfo)
            lt_delta = current_time - launch_time
            running_time_hr = str(lt_delta)

            price = 0.0
            for row_cnt in range(1, total_rows):
                if price_chart_list[row_cnt][0] == region and price_chart_list[row_cnt][1] == instance_type :
                    price = float(price_chart_list[row_cnt][2]) * (lt_delta.total_seconds()/3600)
            insts = insts +'\n \t --> '+instance.id+ ' , \t ' +running_time_hr+ ' hours , \t ' +str(instance_type)+ ' , \t   $'+str(price)             
            print('Instance : ' + instance.id  + ', Running Time : ' + running_time_hr + ', Instance Type : ' + str(instance_type) + ', Price : ' + str(price))
    message_price = 'The following is the list of '+str(instance_identifier)+' instances from the '+str(stack_identifier)+' environment with the Cost Statistics :: \n\t\t\t\t INSTANCE ID  \t||\t  TOTAL RUNNING TIME \t||\t  INSTANCE TYPE \t||\t   PRICE in ($) :- ' + insts
        
    return elicit(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message_price
        }
    )


    
#---------------------------------------- Listing all the services in Ambari--------------------------------------------------
    
def services_list(intent_request):
    
    instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    print instance_identifier
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
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
               if('Ambari' in (response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Value']) or ('ambari' in (response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Value'] ))):
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
    service_list_0 = check_service_list(instance_id)
    #service_list_1 = check_service_list(instance_id)
    str3 = ', \n'.join(service_list_0)
    #print service_list_1
    
    #return check_service_list(instance_id)
    return elicit(
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Hers is list of services which are present in '+str(stack_identifier)+' environment: ' + str3
            }
            )    

# Checking the list of services in Ambari
            
def check_service_list(ip):
    try:
        print("getting service list")
        response_instance = ec2_client.describe_instances( InstanceIds = [ip])
        #print("DNS: " + response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName'])
        #base_url = 'https://'+response_instance['Reservations'][0]['Instances'][0]['PrivateDnsName']+':8080/api/v1/clusters'
        #print base_url
        print("Public DNS: " + response_instance['Reservations'][0]['Instances'][0]['PublicDnsName'])
        base_url2 = 'http://'+response_instance['Reservations'][0]['Instances'][0]['PublicDnsName']+':8080/api/v1/clusters'
        print base_url2
        r = requests.get(base_url2, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
        cluster_name = r.json()['items'][0]['Clusters']['cluster_name']
        print ("cluster name")
        print (cluster_name)
        base_url_services = 'http://'+response_instance['Reservations'][0]['Instances'][0]['PublicDnsName']+':8080/api/v1/clusters/'+cluster_name+'/services'
        r_services = requests.get(base_url_services, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
        print(r_services.json())
        service_list = []
        #total_serv_count = 0
        for i in range(0,len(r_services.json()['items'])):
            service_list.append(r_services.json()['items'][i]['ServiceInfo']['service_name'])
            #total_serv_count + = 1
        print (service_list)
        #print (total_serv_count)
        
    except Exception as e:
        print(e)
    
    return (service_list)#,total_serv_count)
    #return (service_list,total_serv_count)

# Checking the health of services in Ambari

def status_list_services(intent_request):
    #instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    #print instance_identifier
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
    #response_describe = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name','Values': ['*'+instance_identifier+'*']}])
    instance_identifier= "Ambari"
    print instance_identifier
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
               if('Ambari' in (response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Value']) or ('ambari' in (response_describe['Reservations'][i]['Instances'][j]['Tags'][k]['Value'] ))):
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
    print 'There are a total of  '+str(total_instances)+'  Instances and they are as follows:-'+'\n'+str2
    service_list = check_service_list(instance_id)
    #get total number of sevices present in hdp
    service_list_count = len(service_list)
    print service_list_count
    print service_list
    print instance_id
    status_with_service = check_service_state(service_list,instance_id)
    
    running_service_list=list()
    stop_service_list = list()
    for key, value in status_with_service.iteritems():
        if value == 'STARTED' or value == 'Started':
            running_service_list.append(key)
        elif value == 'INSTALLED' or value == 'Installed':
            poweredoff_service_list.append(key)
        else:
            stop_service_list.append(key)
        
    print 'count of list of services running is : ' + str(len(running_service_list)) 
    print 'count of list of services stop is : ' + str(len(stop_service_list))
    print 'count of list of '
    str3 = json.dumps(status_with_service)
    #print 'There are a total of ' ' Services and 
    
    #return check_service_list(instance_id)
    message_health_status = str(stack_identifier)+" Environment Current Status : \n Currently we have a total of "+str(service_list_count)+" services in the "+ str(stack_identifier)+" environment. \n From the above,  "+str(len(running_service_list))+" services are HEALTHY and "+str(len(stop_service_list))+" services are UNHEALTHY !!!  \n The detailed list of services are : \n"+ str3
    return elicit(
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': message_health_status #'Here is list of services alongwith their State: ' + str3
            }
            )        
    
# Checking the list of services along with their state in Ambari

    
def check_service_state(service_list,instance_id):
    try:
        response_instance = ec2_client.describe_instances( InstanceIds = [instance_id])
        print("DNS: " + response_instance['Reservations'][0]['Instances'][0]['PublicDnsName'])
        base_url = 'http://'+response_instance['Reservations'][0]['Instances'][0]['PublicDnsName']+':8080/api/v1/clusters'
        r = requests.get(base_url, auth=HTTPBasicAuth(ambariUser, ambariPass), verify=False)
        cluster_name = r.json()['items'][0]['Clusters']['cluster_name']
        
        print("checking the State of the services ")
        service_dict = {}
        #GET api/v1/clusters/c1/services/HDFS?fields=ServiceInfo/state
        for service in service_list:
            print('Turning Off maintenance mode ' + service)
            maintenanceURL = 'http://'+response_instance['Reservations'][0]['Instances'][0]['PublicDnsName']+':8080/api/v1/clusters/'+cluster_name+'/services/'+service
            stopdata = {"RequestInfo":{"context":"Turn Off Maintenance Mode"},"Body":{"ServiceInfo":{"maintenance_state":"OFF"}}}
            headers = {"X-Requested-By": "ambari"}
            response = requests.put(maintenanceURL, auth=HTTPBasicAuth(ambariUser, ambariPass), data=json.dumps(stopdata), headers=headers, verify=False)
            print('Maintenance response is')
            print(response)
            #curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Remove Falcon from maintenance mode"}, "Body": {"ServiceInfo": {"maintenance_state": "OFF"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/FALCON
            #print('Service check begins')
            base_url_state = 'http://'+response_instance['Reservations'][0]['Instances'][0]['PublicDnsName']+':8080/api/v1/clusters/'+cluster_name+'/services/'+service+'?fields=ServiceInfo/state'
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
    
# --- Return handler for the different functions ---    

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
        return action_instances(intent_request)
    elif intent_name == 'greetings':
        return greetings(intent_request)
    elif intent_name == 'utilization_statistics':
        return utilization_statistics(intent_request)
    elif intent_name == 'pricing_information':
        return pricing_information(intent_request)
    elif intent_name == 'Status_list_machines':
        return services_list(intent_request)
    elif intent_name == 'status_list_services':
        return status_list_services(intent_request)
    elif intent_name == 'list_all_instances':
        return list_all_instances(intent_request)
    elif intent_name == 'list_all_run_instances':
        return list_all_run_instances(intent_request)
    elif intent_name == 'list_all_stop_instances':
        return list_all_stop_instances(intent_request)
    elif intent_name == 'list_instance_untagged':
        return list_instance_untagged(intent_request)
    elif intent_name == 'list_instance_tagged':
        return list_instance_tagged(intent_request)
    else:
        return close(
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Apologies !!  The request which you are looking for does not support with the current release!! \n\n\n Can I help you with any other request? '
                                      
            }
                     )
    
# --- Main handler ---

def lambda_handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)

# ---End of Main handler ----
    
# ---------------------------------------------------- Old lambda Code ------------- Need to refine ----------------------    

#----------------------    The following is the old code from the old lambda


#--------------------------- List of all the instances in the Account-------------------------------

def list_all_instances(intent_request):
    #instance_action = intent_request['currentIntent']['slots']['instance_actions']
    #instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running','stopped','terminated','pending','stopping','shutting-down']}])
    insts = ""
    counter = 0
    for instance in instances:
        if instance.tags:
                for tag in instance.tags:
                    counter = counter+1
                    if tag['Key'] == 'Name':
                        insts = insts+" , \t "+ "\n -> " +tag['Value']                    
            #if 'Name' in instance.tags:
                #insts = insts+" "+instance.tags['Name']        
        print (instance.id, instance.instance_type, instance.state)
    message_list = 'The following is the List of all the Instances in the '+str(stack_identifier)+' environment :- ' + insts    
    return elicit(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message_list
        }
    )
    

# List of all the running instances

def list_all_run_instances(intent_request):
    #instance_action = intent_request['currentIntent']['slots']['instance_actions']
    #instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    insts = ""
    counter = 0
    for instance in instances:
        if instance.tags:
                for tag in instance.tags:
                    counter = counter+1
                    if tag['Key'] == 'Name':
                        insts = insts+" \t "+ "\n \t --> " +tag['Value'] + ","                    
            #if 'Name' in instance.tags:
                #insts = insts+" "+instance.tags['Name']        
        print (instance.id, instance.instance_type, instance.state)
    message_instances = 'The following is the List of all the Running Instances in the '+str(stack_identifier)+' environment :- ' + insts
    return elicit(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message_instances
        }
    )
    
    
# List of all the stopped instances
    
def list_all_stop_instances(intent_request):
    #instance_action = intent_request['currentIntent']['slots']['instance_actions']
    #instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
    insts = ""
    counter = 0
    for instance in instances:
        if instance.tags:
                for tag in instance.tags:
                    counter = counter+1
                    if tag['Key'] == 'Name':
                        insts = insts+" \t "+ "\n \t --> " +tag['Value'] + ","                    
            #if 'Name' in instance.tags:
                #insts = insts+" "+instance.tags['Name']        
        print (instance.id, instance.instance_type, instance.state)
    message_instances = 'The following is the List of all the Stopped Instances in the '+str(stack_identifier)+' environment :- ' + insts    
    return elicit(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message_instances
        }
    )
    
    
def list_instance_untagged(intent_request):
    #instance_action = intent_request['currentIntent']['slots']['instance_actions']
    #instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
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
                        insts = insts + " \t "+ "\n \t --> " +tag['Value'] + ","
    message_tagged = 'The following is the List of all the Untagged Instances in the '+str(stack_identifier)+' environment :- ' + insts    
                
    return elicit(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message_tagged
        }
    )

# List of all the tagged instances in the account

def list_instance_tagged(intent_request):
    #instance_action = intent_request['currentIntent']['slots']['instance_actions']
    #instance_identifier = intent_request['currentIntent']['slots']['instance_identifiers']
    stack_identifier = intent_request['currentIntent']['slots']['stack_identifiers']
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
    message_tagged = 'The following is the List of all the Tagged Instances in the '+str(stack_identifier)+' environment :- ' + insts
    return elicit(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message_tagged
        }
    )
    
    
