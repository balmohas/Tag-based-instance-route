import json
import boto3
from botocore.exceptions import ClientError
import os

#prerequisite 
#Set below Environment Variables

    #ADMIN_EMAIL user@domain.com --> Let's assume that none of the standard tags set correctly on the instances, 
        #then the script sends an email set for ADMIN_MAIL (Assuming it is a verified email)
    #FROM_EMAIL	donot_response@domain.com  usually customers have email like donot_response@domain.com
    #REGION	us-west-2
    #TAG_NAME1 ServiceOwner
    #TAG_NAME2 SystemsOwner
    #TAG_NAME3 Service 


##This function checks the affected instances with "AWS_EC2_MAINTENANCE_SCHEDULED" under the health system service
# When Health System send an notification to the Health API service, it triggers an Event bridge call, which inturn triggers the lambda function
# This code first check to see if Instance has tag(s) in order such as ServiceOwner, SystemOwner and Service. 
#You can customized them via Environment Variables.
                    ###Business Logic####
#If ServieOwner tag exists then it sends an email associate with tag value (assuming it is a verified email). If ServiceOwner does not exists, it checks for SystemsOwner tag
#and sends an email to email address assocaited with its value (assuming it is a verified email). If both of them are not available, then it checks for Service tag, 
#and sends an email to email address assocaited with its value (assuming it is a verified email). If none of the standard tags are available, then it sends email to the 
#


# you can pull region and tag names associated with the instances via "os" lib
AWS_REGION = os.environ['REGION'] #used with Lambda to get the current region
tagName1 = os.environ['TAG_NAME1'] # You can customize the tag value as per your customer's user case
tagName2 = os.environ['TAG_NAME2'] # You can customize the tag value as per your customer's user case
tagName3 = os.environ['TAG_NAME3'] # You can customize the tag value as per your customer's user case

client = boto3.client('ec2', region_name=AWS_REGION)
error_count = 0

#Buiding framework for notification,

def SESNotification(to_address, instanceId):
    # Create an SES client
    ses = boto3.client('ses',region_name=AWS_REGION)
    response = ''
#Seinding an email
    try:
        response = ses.send_email(
            Source= os.environ["FROM_EMAIL"],
            Destination={
                'ToAddresses': [
                    to_address,
                ]
            },
            Message={
                'Subject': {
                    'Data': f'AWS Health Event - AWS_EC2_MAINTENANCE_SCHEDULED for the instance - {instanceId}'
                },
                'Body': {
                    'Text': {
                        'Data': f'The following instance {instanceId} is up for maintenance, please take an appropriate action'
                    }
                }
            }
        )
    except ses.exceptions.MessageRejected:
        print (f"Please ensure email address is verified and/or has a correct address {to_address}") 
         # exit if error_count (lambda doesn't like sys.exit(0))
        return
    return response

#Retriving tags assocaited with the instance

def describeInstance(instanceId):
    try:
        instances = client.describe_instances(
            InstanceIds=[ 
            instanceId,
            ],
        )   
        ## Find out tages instance
        print (instances['Reservations'][0]['Instances'][0]['Tags'])
        tags = instances['Reservations'][0]['Instances'][0]['Tags']
        tagdict = {}
        #in future Zoom wants to add more tags, they can add them here
        knownTagList = [tagName1, tagName2, tagName3]
        print (f"know tag list is {knownTagList}")
        for x in tags:
            print (f'the key value is {x}')
            if x['Key'] in knownTagList:
                print ((x['Key'] in knownTagList))
                tagdict[x['Key']] = x['Value']
            else:
                print(f"checking for {knownTagList} tags only and ignoring the rest {x['Key']}")
        print(tagdict)
    except ClientError as err:
        print (f'{err} - Please check if instance - {instanceId} exists')
    return tagdict
    
    
def lambda_handler(event, context):
    
    #setting admin email address via env. variable if none of the tags matches, it sends email to emailToAdmin
    emailToAdmin = os.environ["ADMIN_EMAIL"]
    #Get Affected Instance Id
    #print (event['detail']['affectedEntities'][0]['entityValue'])
    INSTANCE_ID = event['detail']['affectedEntities'][0]['entityValue']
    print (f'InstanceIds is {INSTANCE_ID}')
    
    #retreiving tags associated with the instance
    tagdict = describeInstance(INSTANCE_ID)
    print (f'Lenght of the known tags is {len(tagdict)}')
    print (f'tagdict in handler is {tagdict}')
    if len(tagdict) > 0:
        if 'ServiceOwner' in tagdict:
            print(f"ServiceOwner exists {tagdict}")
            SESNotification(tagdict['ServiceOwner'],INSTANCE_ID) 
            return 
        elif 'SystemsOwner' in tagdict:
            print(f"SystemsOwner exists {tagdict}")
            SESNotification(tagdict['SystemOwner'],INSTANCE_ID) 
            return 
        elif 'Service' in tagdict:
            print(f"Service exists {tagdict}")
            SESNotification(tagdict['Service'],INSTANCE_ID) 
            return 
        else:
            #Mising needed tags from affected instance, sending an email to the account Admin set as the Environment Variable "From_EMAIL". 
            #You can change it alias with a couple of admins
            SESNotification( emailToAdmin,INSTANCE_ID) 
            return
    else:
        #Mising needed tags from affected instance, sending an email to the account Admin. I have set an enviornment variable "ADMIN_EMAIL as "yasin.mohammed@zoom.us". 
            #You can change it alias with a couple of admins
            SESNotification( emailToAdmin,INSTANCE_ID)
            return 
    return 'success'