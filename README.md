

**Title**

<u> Using Tag-Based filtering to manage instance Health Monitoring and Alerting at Scale <u>

**Background**

AWS provides customers regular updates on service notifications and planned activities such as operational, security, and billing activity via e-mail to the root account owners and alternate contacts. AWS also provides granular notifications to customers via AWS Health Dashboard, allowing them to fine-tune their alerts on issues relating directly to them. However, as customers grow and add new accounts within AWS Organizations, each of these accounts may generate alerts based on the AWS Health events, and it becomes important to redirect those alerts to the appropriate teams at scale.
Here is the guidance on alerting on AWS infrastructure health events using AWS Health, and fine-tune notifications to fit in to your existing workflows with the right tagging strategy (https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/tagging-best-practices.html) so you can identify resources and direct your alerts to the appropriate areas of responsibility. 

**Architecture**

![alt text]( https://github.com/balmohas/Tag-based-instance-route/blob/main/image.png?raw=true)![image](https://github.com/balmohas/Tag-based-instance-route/assets/93612585/301ad588-5df8-41ec-a395-830dc5226f71)


**Solution Overview** 

This solution checks the affected instances with "AWS_EC2_MAINTENANCE_SCHEDULED" under the health system service. When the Health System sends a notification to the Health API service, it triggers an EventBridge event, which triggers the lambda function. This code checks to see if the unstance has a tag(s) in order, such as ServiceOwner, SystemOwner, and Service. You can customize them via Environment Variables
- TAG_NAME1 = ServiceOwner
- TAG_NAME2 = SystemsOwner
- TAG_NAME3 = Service

**Prerequisite** 

Set the following Environment Variables

- ADMIN_EMAIL = user@domain.com --> Let's assume that none of the standard tags set correctly on the instances, then the script sends an email set for ADMIN_MAIL (Assuming it is a verified email)
 
- FROM_EMAIL	= donot_response@domain.com  usually customers have email like donot_response@domain.com

- REGION	= us-west-2 --> assuming you want to monitor alert the instance for the us-west-2 region. Please choose an appropriate region.

- TAG_NAME1 = ServiceOwner
- TAG_NAME2 = SystemsOwner
- TAG_NAME3 = Service 

**Steps:**

1. Clone this repository.
2. Log into AWS Management Console and navigate to the lambda console. Ensure you are in the *us-west-2* region. If you need to run this lambda function from another account then make sure to change *REGION* Environment Variable accordingly.	
3. Create a lambda function from scratch and copy the code from "tag_based_instance_routing.py". **NOTE** Please add appropriate region and the AWS account number for the policy.
4. Ensure you have add Environment Variables as mentioned in the Prerequisite.
5. Create an Lambda Execution Role using the policy *lambda_execution_role.json* and add it to the function.
6. Create an Event bridge using custom rule and set the target as the lambda function from the step#3 -
   {
  "source": ["aws.health"],
  "detail-type": ["AWS Health Event"],
  "detail": {
    "service": ["EC2"],
    "eventTypeCategory": ["scheduledChange"]
  }
}


**How Lambda function works**


If tag TAG_NAME1 exists on the instance then it sends an email associate with its value (assuming it is a verified email). If TAG_NAME1 does not exists, it checks for TAG_NAME2 tag and sends an email to email address assocaited with its value (assuming it is a verified email). If both of them are not available, then it checks for TAG_NAME3 and sends an email to email address assocaited with its value (assuming it is a verified email). If none of the standard tags are available, then it sends email to the email associated with the ADMIN_EMAIL Environment Variable.
 
