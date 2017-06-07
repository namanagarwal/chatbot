import boto3
ec2 = boto3.resource('ec2')
def lambda_handler(event, context):
    # TODO implement
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
    for instance in instances:
        print (instance.id, instance.instance_type, instance.state)
    return close(
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks! The following is the list of details of the Instances as requested.'
                        + '\n Instance ID: '+instance.id    
                        + '\n Instance State: '+ instance.state
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