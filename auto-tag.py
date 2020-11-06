import json
import boto3
import logging
import time

from datetime import date
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ec2_source = 'aws.ec2'

###############################################################

# default entry point

def lambda_handler(event, context):

    logger.info('Received event: [{}]'.format(json.dumps(event, indent=2, default=str)))

    

    event_source = event['source']

    file_contents = "ResourceType, ResourceId, OtherDetails\n"

    if event_source == ec2_source:

        file_contents = file_contents + ec2_tag(event,file_contents)

    logger.info('file_contents: [{}]'.format(str(file_contents)))

############################################################### 

# tag the ec2 instances

def ec2_tag(event, file_contents):

    detail = event['detail']

    myInstance = detail['responseElements']['instancesSet']['items'][0]['instanceId']

    eventInfo = extract_event_details(event)

    try:

        file_contents = file_contents + "EC2," + myInstance + ", Tagged\n"

        create_tags('ec2', myInstance, eventInfo)

        return file_contents

    except Exception as e:

        logger.error('Something went wrong: [{}]'.format(str(e)))

        

    return file_contents

    

###############################################################

# extract details from event

def extract_event_details(event):

    detail = event['detail']

    eventname = detail['eventName']

    eventtime = detail['eventTime']

    principal = detail['userIdentity']['principalId']

    userType = detail['userIdentity']['type']

    if userType == 'IAMUser':

        user = detail['userIdentity']['userName']

    else:

        user = principal.split(':')[1]

    eventInfo = {

        'creator': user, 

        'creation_date': eventtime

    }

    return eventInfo

###############################################################


def create_tags(service, instanceId, eventInfo):    

    # create the client to service the call

    client = boto3.client(service)

    

    if (service == 'ec2'):

        # this call will overwrite existing tags, you could check and decide based on the

        # following

        # response = client.describe_tags(

        # Filters=[

        # {

       #            'Name': 'resource-id',

       #     'Values': [

       #         instanceId

       #     ],

       # },

       # ],

       #     )

        client.create_tags(

            Resources=[

                instanceId,

            ],

            Tags=[
                {
                    'Key': 'owner',
                    'Value': eventInfo['creator']
                },
                {
                    'Key': 'creation_date',
                    'Value': eventInfo['creation_date']
                },
                {
                    'Key': 'Environment',
                    'Value': ''
                },
                {
                    'Key': 'Project',
                    'Value': ''
                },
                {
                    'Key': 'Charge_Code',
                    'Value': ''
                }

            ]

        )

        

###############################################################