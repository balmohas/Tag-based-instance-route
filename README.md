

**Title**

<u> Using Tag-Based filtering to manage instance Health Monitoring and Alerting at Scale <u>

**Background**

AWS provides customers regular updates on service notifications and planned activities such as operational, security, and billing activity via e-mail to the root account owners and alternate contacts. AWS also provides granular notifications to customers via AWS Health Dashboard, allowing them to fine-tune their alerts on issues relating directly to them. However, as customers grow and add new accounts within AWS Organizations, each of these accounts may generate alerts based on the AWS Health events, and it becomes important to redirect those alerts to the appropriate teams at scale.

Here is the guidance on alerting on AWS infrastructure health events using AWS Health, and fine-tune notifications to fit in to your existing workflows with the right tagging strategy (https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/tagging-best-practices.html) so you can identify resources and direct your alerts to the appropriate areas of responsibility. 

**Architecture**

![Alt text](/Users/balmohas/Documents/Ballu/Code/health)

**Solution Overview** 
This solution checks the affected instances with "AWS_EC2_MAINTENANCE_SCHEDULED" under the health system service. When the Health System sends a notification to the Health API service, it triggers an Event bridge call, which triggers the lambda function. This code checks to see if the unstance has a tag(s) in order, such as ServiceOwner, SystemOwner, and Service. You can customize them via Environment Variables
- TAG_NAME1 ServiceOwner
- TAG_NAME2 SystemsOwner
- TAG_NAME3 Service

**Prerequisite** 
Set the following Environment Variables

- ADMIN_EMAIL user@domain.com --> Let's assume that none of the standard tags set correctly on the instances, then the script sends an email set for ADMIN_MAIL (Assuming it is a verified email)
- FROM_EMAIL	donot_response@domain.com  usually customers have email like donot_response@domain.com
- REGION	us-west-2 --> assuming you want to monitor alert the instance for the us-west-2 region. Please choose an appropriate region.
- TAG_NAME1 ServiceOwner
- TAG_NAME2 SystemsOwner
- TAG_NAME3 Service 

Steps:
1. 
Download the tag_based_instance_routing.py and copy 
lambda_function.py.
lambda_execution_role.json (Execution role for lambda)
You have set some environment variables
ADMIN_EMAIL   yasin@zoom.com # this is usually @info@example.com or info@amazon.com
FROMEMAIL       yasin@zoom.com #this is the email of the admin - for ex: yasin@zoom.com
REGION us-west-2 # lambda function region.
This is how the lambda function works
#Here is the logic for the flow -
#For this function to work, you need to make sure that the EC2 instance has at the minimum one of these tags for
ServiceOwner --> Email Address
SystemOwner --> Email Address
Service --> Email Address (Since I don’t have the logic from you, I assume to be an email and coded. I hope you can have your engineers to add logic for mapping between service principals and email and update the attached code.
 
Script checks in the order
if ServiceOwner tag exists, if it does and have an email address, it sends an email to the ServiceOwner and then exit.
If it does not, it checks out for SystemOwner tag exists, if it does and have an email address, it sends an email to the SystemOwner and then exit.
If it does not, it checks out for Service tag exists, if it does and have an email address, it sends an email to the Service and then exit.
If none of the above tags available, it sends an email to a user set as the Environment variable --> FROMEMAIL.
 
