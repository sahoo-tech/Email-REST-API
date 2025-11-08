import json
import os
import re
import logging
from typing import Dict, Any, Tuple
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SES client
ses_client = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'us-east-1'))


def is_valid_email(email: str) -> bool:

    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(email_regex, email))


def validate_request_body(body: Dict[str, Any]) -> Tuple[bool, str]:

    if not body:
        return False, 'Request body is required'
    
    # Check for required fields
    required_fields = ['receiver_email', 'subject', 'body_text']
    for field in required_fields:
        if field not in body:
            return False, f'Missing required field: {field}'
    
    receiver_email = body.get('receiver_email')
    subject = body.get('subject')
    body_text = body.get('body_text')
    
    # Validate email format
    if not is_valid_email(receiver_email):
        return False, 'Invalid email format for receiver_email'
    
    # Validate field types
    if not isinstance(subject, str) or not isinstance(body_text, str):
        return False, 'subject and body_text must be strings'
    
    # Validate field lengths
    if not subject.strip() or not body_text.strip():
        return False, 'subject and body_text cannot be empty'
    
    return True, ''


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(body)
    }


def send_email(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

    logger.info(f'Received event: {json.dumps(event)}')
    
    try:
        # Parse request body
        try:
            request_body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError as e:
            logger.error(f'JSON parse error: {str(e)}')
            return create_response(400, {
                'success': False,
                'message': 'Invalid JSON in request body',
                'error': str(e)
            })
        
        # Validate request body
        is_valid, error_message = validate_request_body(request_body)
        if not is_valid:
            logger.error(f'Validation error: {error_message}')
            return create_response(400, {
                'success': False,
                'message': error_message
            })
        
        receiver_email = request_body['receiver_email']
        subject = request_body['subject']
        body_text = request_body['body_text']
        sender_email = os.environ.get('SENDER_EMAIL')
        
        # Check if sender email is configured
        if not sender_email:
            logger.error('SENDER_EMAIL environment variable not set')
            return create_response(500, {
                'success': False,
                'message': 'Server configuration error: sender email not configured'
            })
        
        # Send email via SES
        logger.info(f'Sending email to {receiver_email} with subject: {subject}')
        
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [receiver_email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        message_id = response['MessageId']
        logger.info(f'Email sent successfully. MessageId: {message_id}')
        
        return create_response(200, {
            'success': True,
            'message': 'Email sent successfully',
            'messageId': message_id,
            'data': {
                'to': receiver_email,
                'subject': subject
            }
        })
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f'SES ClientError: {error_code} - {error_message}')
        
        # Handle specific SES errors
        if error_code == 'MessageRejected':
            return create_response(400, {
                'success': False,
                'message': 'Email rejected by SES',
                'error': error_message
            })
        
        if error_code in ['MailFromDomainNotVerified', 'EmailAddressNotVerified']:
            return create_response(500, {
                'success': False,
                'message': 'Sender email not verified in AWS SES',
                'error': error_message
            })
        
        # Generic SES error
        return create_response(500, {
            'success': False,
            'message': 'Failed to send email',
            'error': error_message
        })
        
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return create_response(500, {
            'success': False,
            'message': 'Internal server error',
            'error': str(e)
        })