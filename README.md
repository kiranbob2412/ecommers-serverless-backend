# 🛒 Serverless E-Commerce Backend Platform

A production-grade, event-driven serverless e-commerce backend built entirely on AWS — designed for scale, security, and zero operational overhead.

## 📐 Architecture Overview

```
                          ┌─────────────┐
                          │   Client    │
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │  CloudFront │  CDN + Edge Caching
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │ API Gateway │  REST API + Auth
                          └──────┬──────┘
                                 │
               ┌─────────────────┼─────────────────┐
               │                 │                 │
        ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
        │   Lambda    │  │   Lambda    │  │   Lambda    │
        │  Products   │  │   Orders    │  │    Users    │
        └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
               │                 │                 │
        ┌──────▼─────────────────▼─────────────────▼──────┐
        │                    DynamoDB                      │
        │         products | orders | users                │
        └───────────────────────┬──────────────────────────┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
        ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
        │     S3      │  │     SNS     │  │  CloudWatch │
        │   Images    │  │  + SQS      │  │  + X-Ray    │
        └─────────────┘  └──────┬──────┘  └─────────────┘
                                │
                         ┌──────▼──────┐
                         │   Lambda    │
                         │Notification │
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐
                         │     SES     │  Email Delivery
                         └─────────────┘
```

## ✨ Features

- 🔐 **Secure Authentication** — Amazon Cognito JWT-based auth with self-registration
- ⚡ **Event-Driven** — S3 uploads trigger Lambda automatically, zero polling
- 🛍️ **Full CRUD APIs** — Products, Orders, Users with proper HTTP methods
- 📧 **Email Notifications** — SES order confirmation emails via SNS → SQS → Lambda pipeline
- 📊 **Observability** — CloudWatch dashboards, alarms, and X-Ray distributed tracing
- 🚀 **Auto-scaling** — Serverless by design, handles any traffic volume
- 💰 **Cost-Optimized** — Pay-per-execution, no idle compute costs
- 🌍 **Global CDN** — CloudFront edge caching for low-latency worldwide

## 🛠️ AWS Services Used

| Service | Purpose | Free Tier |
|---|---|---|
| **Amazon Cognito** | User auth + JWT tokens | 50K MAU free |
| **API Gateway** | REST API endpoints | 1M calls/month |
| **AWS Lambda** | Serverless business logic (Python 3.12) | 1M calls/month |
| **Amazon DynamoDB** | NoSQL database | 25GB storage |
| **Amazon S3** | Product image storage | 5GB storage |
| **Amazon CloudFront** | CDN + edge caching | 1TB transfer |
| **Amazon SNS** | Push notifications | 1M publishes |
| **Amazon SQS** | Message queue (decoupled pipeline) | 1M requests |
| **Amazon SES** | Transactional email delivery | 62K emails/month |
| **Amazon EventBridge** | Cron scheduler (daily reports) | 1M events |
| **AWS Step Functions** | Order workflow orchestration | 4K transitions |
| **Amazon CloudWatch** | Monitoring + alerts + dashboards | 10 metrics free |
| **AWS X-Ray** | Distributed tracing | 100K traces/month |
| **IAM** | Least-privilege access control | Always free |

## 📦 API Endpoints

### Products
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/products` | Create a new product |
| `GET` | `/products` | Get all products |
| `GET` | `/products/{product_id}` | Get single product |
| `PUT` | `/products/{product_id}` | Update product |
| `DELETE` | `/products/{product_id}` | Delete product |

### Orders
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/orders` | Place a new order |
| `GET` | `/orders` | Get all orders |
| `GET` | `/orders/{order_id}` | Get single order |
| `PUT` | `/orders/{order_id}` | Update order status |

### Users
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/users/register` | Register new user |
| `POST` | `/users/login` | Login + get JWT token |
| `GET` | `/users/{user_id}` | Get user profile |

## 🗄️ DynamoDB Schema

### Products Table
```json
{
  "product_id": "uuid (PK)",
  "name": "string",
  "price": "number",
  "description": "string",
  "stock": "number",
  "created_at": "ISO timestamp"
}
```

### Orders Table
```json
{
  "order_id": "uuid (PK)",
  "user_id": "string",
  "products": "list",
  "total_amount": "number",
  "status": "PENDING | CONFIRMED | SHIPPED | DELIVERED",
  "created_at": "ISO timestamp"
}
```

### Users Table
```json
{
  "user_id": "uuid (PK)",
  "email": "string",
  "name": "string",
  "cognito_sub": "string",
  "created_at": "ISO timestamp"
}
```

## 🔐 Security

- **Cognito User Pool** — JWT token-based authentication
- **IAM Least Privilege** — Each Lambda has only required permissions
- **Private S3 Bucket** — No public access, signed URLs for image delivery
- **API Gateway Authorizer** — Every endpoint protected with Cognito JWT

## 🚀 Deployment

### Prerequisites
```bash
pip install boto3
aws configure  # Set up AWS credentials
```

### 1. Create DynamoDB Tables
```bash
aws dynamodb create-table \
  --table-name products \
  --attribute-definitions AttributeName=product_id,AttributeType=S \
  --key-schema AttributeName=product_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --table-name orders \
  --attribute-definitions AttributeName=order_id,AttributeType=S \
  --key-schema AttributeName=order_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --table-name users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### 2. Create Cognito User Pool
```bash
aws cognito-idp create-user-pool \
  --pool-name ecommerce-user-pool \
  --auto-verified-attributes email
```

### 3. Deploy Lambda Functions
```bash
zip products.zip products_handler.py
aws lambda create-function \
  --function-name products-handler \
  --runtime python3.12 \
  --handler products_handler.lambda_handler \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/LambdaEcommerceRole \
  --zip-file fileb://products.zip
```

### 4. Configure S3 Notification
```bash
aws s3api put-bucket-notification-configuration \
  --bucket your-bucket-name \
  --notification-configuration file://notification.json
```

### 5. Test the API
```bash
# Create a product
curl -X POST https://your-api-id.execute-api.ap-south-1.amazonaws.com/prod/products \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 999.99, "stock": 10}'

# Get all products
curl https://your-api-id.execute-api.ap-south-1.amazonaws.com/prod/products
```

## 📊 Monitoring

- **CloudWatch Dashboard** — Lambda invocations, errors, duration
- **CloudWatch Alarms** — Alert on error rate > 1%
- **X-Ray Tracing** — End-to-end request tracing across all services
- **CloudWatch Logs** — Centralized logging for all Lambda functions

## 🌱 Roadmap

- [ ] API Gateway → Lambda → Step Functions order workflow
- [ ] EventBridge daily sales report → SES email
- [ ] CloudFront + WAF for DDoS protection
- [ ] Multi-region active-active setup
- [ ] Terraform IaC for one-command deployment
- [ ] GitHub Actions CI/CD pipeline
- [ ] Redis (ElastiCache) for session caching
- [ ] OpenSearch for product search

## 👨‍💻 Author
kiranbob cloud engineer
Built with ❤️ using AWS Serverless stack — 100% Free Tier compatible!
