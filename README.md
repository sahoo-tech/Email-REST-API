# Serverless Email API - Complete Guide

## Project Overview

This project implements a **REST API on AWS Lambda** that sends emails using Amazon SES (Simple Email Service). The API is built with the **Serverless Framework** and supports both **Node.js** and **Python** implementations.

**Key Features:**
- ✅ Sends emails via AWS SES
- ✅ HTTP API Gateway integration
- ✅ Comprehensive error handling
- ✅ Input validation (email format, required fields)
- ✅ Proper HTTP status codes (200, 400, 500)
- ✅ CORS enabled for cross-origin requests
- ✅ Environment-based configuration
- ✅ Production-ready code

---

## Architecture

```
Client (curl/Postman/Frontend)
           ↓
    API Gateway (HTTP API)
           ↓
    AWS Lambda Function
           ↓
    Amazon SES
           ↓
    Email Recipient
```

---

## Prerequisites

Before you start, ensure you have:

1. **AWS Account** - with appropriate IAM permissions
2. **Node.js** - v14 or higher (for Node.js version or package management)
3. **Python** - v3.11 or higher (for Python version)
4. **AWS CLI** - installed and configured with credentials
5. **Serverless Framework** - installed globally

### Installation Commands

```bash
# Install Node.js (if not already installed)
# Visit: https://nodejs.org/

# Install Serverless Framework globally
npm install -g serverless

# Install AWS CLI
# Windows: https://awscli.amazonaws.com/AWSCLIV2.msi
# macOS: brew install awscli
# Linux: curl + unzip (see detailed guide)
```

---

## AWS Setup

### Step 1: Create IAM User

1. Log into AWS Console at https://console.aws.amazon.com/
2. Navigate to **IAM** → **Users** → **Create user**
3. Enable **Programmatic access**
4. Attach these policies:
   - `AWSLambdaFullAccess`
   - `AmazonAPIGatewayAdministrator`
   - `AmazonSESFullAccess`
   - `CloudFormationFullAccess`
   - `IAMFullAccess`
   - `AmazonS3FullAccess`
5. Save **Access Key ID** and **Secret Access Key**

### Step 2: Configure AWS CLI

```bash
aws configure
```

Enter when prompted:
```
AWS Access Key ID: YOUR_ACCESS_KEY_ID
AWS Secret Access Key: YOUR_SECRET_ACCESS_KEY
Default region name: us-east-1
Default output format: json
```

Verify configuration:
```bash
aws sts get-caller-identity
```

### Step 3: Verify SES Email

Before sending emails, verify your sender email address in SES:

```bash
# Verify sender email
aws ses verify-email-identity --email-address your-email@example.com --region us-east-1

# Check verification status (should show VerificationStatus: Success)
aws ses get-identity-verification-attributes --identities your-email@example.com --region us-east-1
```

Check your inbox and click the verification link from AWS.

---

## Project Setup

### Directory Structure

```
email-api/
├── handler.js (or handler.py for Python)
├── serverless.yml
├── package.json (Node.js) or requirements.txt (Python)
├── .gitignore
└── README.md
```

### Step 1: Create Project Directory

```bash
mkdir email-api
cd email-api
```

### Step 2: Create Files

Copy the following files from the provided templates:

#### **serverless.yml**
```yaml
service: email-api

frameworkVersion: '3'

provider:
  name: aws
  runtime: nodejs18.x  # or python3.11 for Python version
  region: us-east-1
  environment:
    SENDER_EMAIL: 'your-verified-email@example.com'
    AWS_REGION: 'us-east-1'
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - ses:SendEmail
            - ses:SendRawEmail
          Resource: '*'

functions:
  sendEmail:
    handler: handler.sendEmail
    timeout: 30
    events:
      - httpApi:
          path: /send-email
          method: post

plugins:
  - serverless-offline
```

#### **handler.js** (Node.js version)
See the provided template file.

#### **handler.py** (Python version)
See the provided template file.

#### **package.json** (Node.js only)
```json
{
  "name": "email-api",
  "version": "1.0.0",
  "description": "Serverless email API using AWS SES",
  "main": "handler.js",
  "scripts": {
    "deploy": "serverless deploy",
    "offline": "serverless offline start",
    "logs": "serverless logs -f sendEmail -t"
  },
  "dependencies": {
    "aws-sdk": "^2.x.x"
  },
  "devDependencies": {
    "serverless": "^3.x.x",
    "serverless-offline": "^13.x.x"
  }
}
```

#### **requirements.txt** (Python only)
```
boto3==1.28.x
```

### Step 3: Update Configuration

Edit `serverless.yml` and replace:
```yaml
SENDER_EMAIL: 'your-verified-email@example.com'  # Your verified SES email
```

### Step 4: Install Dependencies

**For Node.js:**
```bash
npm install
```

**For Python:**
```bash
pip install -r requirements.txt
```

---

## API Usage

### Endpoint

**POST** `https://{api-id}.execute-api.{region}.amazonaws.com/send-email`

### Request Body

```json
{
  "receiver_email": "recipient@example.com",
  "subject": "Email Subject",
  "body_text": "Email body text content here."
}
```

### Response (Success - 200)

```json
{
  "success": true,
  "message": "Email sent successfully",
  "messageId": "0100018c...",
  "data": {
    "to": "recipient@example.com",
    "subject": "Email Subject"
  }
}
```

### Response (Error - 400)

```json
{
  "success": false,
  "message": "Invalid email format",
  "statusCode": 400
}
```

### Response (Error - 500)

```json
{
  "success": false,
  "message": "Internal server error",
  "statusCode": 500
}
```

---

## Testing Locally

### Option 1: Using Serverless Offline (Node.js)

```bash
# Install dependency
npm install

# Start local server
serverless offline start
```

The API will be available at `http://localhost:3000`

### Test with curl

```bash
curl -X POST http://localhost:3000/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_email": "test@example.com",
    "subject": "Test Email",
    "body_text": "Hello from local testing!"
  }'
```

### Option 2: Python Local Test Script

Create `test_local.py`:

```python
#!/usr/bin/env python3
import json
from handler import send_email

test_event = {
    'body': json.dumps({
        'receiver_email': 'recipient@example.com',
        'subject': 'Test Email',
        'body_text': 'Testing locally'
    })
}

class Context:
    function_name = 'test-function'
    memory_limit_in_mb = 128

if __name__ == '__main__':
    response = send_email(test_event, Context())
    print(json.dumps(json.loads(response['body']), indent=2))
```

Run with:
```bash
python test_local.py
```

---

## Deployment to AWS

### Deploy to Development

```bash
serverless deploy
```

### Deploy to Production

```bash
serverless deploy --stage prod
```

### Using Specific AWS Profile

```bash
serverless deploy --aws-profile my-profile-name
```

### Get Deployment Info

```bash
serverless info
```

This will show your API endpoint URL.

---

## Testing Deployed API

### Get Your API URL

```bash
serverless info
```

Look for the `endpoint` output. Example:
```
endpoint: POST - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/send-email
```

### Test with curl

```bash
curl -X POST https://YOUR-API-URL/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_email": "recipient@example.com",
    "subject": "Production Test",
    "body_text": "Testing from production!"
  }'
```

### Test with Postman

1. Open Postman
2. Create new **POST** request
3. URL: `https://YOUR-API-URL/send-email`
4. Headers:
   - `Content-Type: application/json`
5. Body (raw JSON):
   ```json
   {
     "receiver_email": "recipient@example.com",
     "subject": "Test",
     "body_text": "Hello"
   }
   ```
6. Click **Send**

---

## Troubleshooting

### Error: "AWS credentials missing or invalid"

**Solution:**
```bash
aws configure
```

Enter your Access Key ID and Secret Access Key.

Verify:
```bash
aws sts get-caller-identity
```

### Error: "Email address is not verified"

**Solution:**
You're in SES sandbox mode. Verify both sender and receiver emails:

```bash
aws ses verify-email-identity --email-address sender@example.com --region us-east-1
aws ses verify-email-identity --email-address receiver@example.com --region us-east-1
```

### Error: "Request body is required"

**Solution:**
Ensure your curl command includes the JSON body with `-d` flag:

```bash
curl -X POST http://localhost:3000/send-email \
  -H "Content-Type: application/json" \
  -d '{"receiver_email":"test@example.com","subject":"Test","body_text":"Hello"}'
```

### Error: "Lambda timeout"

**Solution:**
1. Ensure AWS credentials are configured: `aws configure`
2. Increase timeout in `serverless.yml`:
   ```yaml
   timeout: 30
   ```
3. Verify SES region matches AWS CLI region

### Error: "Access Denied" during deployment

**Solution:**
Your IAM user lacks permissions. Add these policies:
- `AWSLambdaFullAccess`
- `AmazonAPIGatewayAdministrator`
- `AmazonSESFullAccess`
- `CloudFormationFullAccess`
- `IAMFullAccess`

### SES Sandbox Mode Restrictions

**Problem:** Can only send emails to verified addresses

**Solutions:**
1. **Option A:** Verify all recipient emails in SES (limited testing)
2. **Option B:** Request production access in SES Console
   - Go to **Sending Statistics**
   - Click **Request a Sending Limit Increase**
   - Fill out the form
   - AWS typically approves within 24-48 hours

---

## SES Sandbox Mode vs Production

### Sandbox Mode (Default)
- ✅ Free testing
- ❌ Can only send to verified emails
- ❌ Limited sending rate (1 email/second, 200/day)
- ❌ Cannot send to arbitrary recipients

### Production Mode
- ✅ Send to any email address
- ✅ Higher sending limits
- ✅ Better delivery rates
- ❌ Requires production access request
- ❌ May incur costs if exceeding free tier

---

## Monitoring and Logging

### View Real-time Logs

```bash
serverless logs -f sendEmail -t
```

### View CloudWatch Logs in AWS Console

1. Go to AWS Console
2. Navigate to **CloudWatch** → **Log Groups**
3. Find `/aws/lambda/email-api-dev-sendEmail`
4. Check recent log events

### Check SES Sending Statistics

```bash
aws ses get-send-statistics --region us-east-1
```

---

## Cost Estimation

| Service | Free Tier | Overage Cost |
|---------|-----------|--------------|
| Lambda | 1M requests/month + 400K GB-seconds | $0.20 per 1M requests |
| API Gateway | 1M requests/month | $3.50 per 1M requests |
| SES | 62K emails/month | $0.10 per 1K emails |

**Typical monthly cost for low-volume:** $0 (within free tier)

---

## Cleanup

### Remove Deployment from AWS

```bash
serverless remove
```

This will delete:
- Lambda function
- API Gateway endpoint
- CloudFormation stack
- CloudWatch log groups

---

## Security Best Practices

1. **Never commit AWS credentials** - `.gitignore` is set up for this
2. **Use IAM roles** - In production, use Lambda execution roles instead of access keys
3. **Rotate access keys** - Regularly rotate IAM user credentials
4. **Enable MFA** - On your IAM user account
5. **Use environment variables** - For sensitive data like `SENDER_EMAIL`
6. **Validate all inputs** - Code already does this
7. **Use HTTPS only** - API Gateway automatically uses HTTPS
8. **Monitor costs** - Set up AWS billing alerts

---

## Environment Variables

You can set environment variables per stage:

```yaml
provider:
  environment:
    SENDER_EMAIL: 'default@example.com'
    
  # Different per stage
stages:
    dev:
      environment:
        SENDER_EMAIL: 'dev@example.com'
    prod:
      environment:
        SENDER_EMAIL: 'prod@example.com'
```

Deploy to specific stage:
```bash
serverless deploy --stage prod
```

---

## Integration Examples

### React Frontend

```javascript
const sendEmail = async (email, subject, message) => {
  const response = await fetch('https://YOUR-API-URL/send-email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      receiver_email: email,
      subject: subject,
      body_text: message
    })
  });
  return response.json();
};
```

### Python Backend

```python
import requests

def send_email(email, subject, message):
    response = requests.post(
        'https://YOUR-API-URL/send-email',
        json={
            'receiver_email': email,
            'subject': subject,
            'body_text': message
        }
    )
    return response.json()
```

---

## Support & Issues

For issues or questions:

1. Check **Troubleshooting** section above
2. Review AWS SES documentation: https://docs.aws.amazon.com/ses/
3. Check Serverless Framework docs: https://www.serverless.com/framework/docs
4. Enable debug mode: `serverless deploy --debug`

---

## License

This project is provided as-is for educational and development purposes.

---

## Next Steps

1. ✅ Set up AWS account and IAM user
2. ✅ Configure AWS CLI
3. ✅ Create project files
4. ✅ Deploy to AWS
5. ✅ Test with curl/Postman
6. ✅ Integrate with your application
7. ✅ Monitor and maintain

Happy coding! 🚀
