# Serverless URL Shortener

A fully serverless URL shortener built on AWS using Lambda, API Gateway, and DynamoDB. Submit a long URL and get back a short one that redirects to the original when visited.

## Architecture

```
                POST /shorten
Client  ────────────────────────►  API Gateway  ────►  Lambda (createShortUrl)  ────►  DynamoDB
                                                                                          (store shortId + longUrl)

                GET /{shortId}
Client  ────────────────────────►  API Gateway  ────►  Lambda (redirectShortUrl) ────►  DynamoDB
                                                                                          (lookup shortId)
                                         │
                                         ▼
                                  301 Redirect to original URL
```

## Tech Stack

- **AWS Lambda** (Python) — business logic for creating and redirecting URLs
- **API Gateway (HTTP API)** — exposes REST endpoints
- **DynamoDB** — stores the mapping between short IDs and original URLs
- **IAM** — least-privilege-style execution roles for each Lambda

## How It Works

1. **Create a short URL** — `POST /shorten` with a JSON body `{ "url": "https://example.com" }`. The Lambda generates a random 6-character ID, stores it in DynamoDB, and returns the short URL.
2. **Use the short URL** — `GET /{shortId}` looks up the ID in DynamoDB and returns a `301` redirect to the original URL.

## Setup

### 1. Create the DynamoDB table
- Table name: `UrlShortener`
- Partition key: `shortId` (String)
- Capacity mode: On-demand

### 2. Create two Lambda functions
- `createShortUrl` — handles URL creation (see `createShortUrl/lambda_function.py`)
- `redirectShortUrl` — handles redirection (see `redirectShortUrl/lambda_function.py`)
- Runtime: Python 3.13+
- Attach `AmazonDynamoDBFullAccess` to each function's execution role (for learning purposes — in production, use a scoped least-privilege policy instead)

### 3. Create an HTTP API in API Gateway
- Add two routes:
  - `POST /shorten` → integrate with `createShortUrl`
  - `GET /{shortId}` → integrate with `redirectShortUrl`
- Deploy to the `$default` stage with auto-deploy enabled

## Demo

**Creating a short URL:**

![Create short URL](screenshots/create-url-success.png)

**Redirecting to the original URL:**

![Redirect success](screenshots/redirect-success.png)

**DynamoDB table storing the mapping:**

![DynamoDB table](screenshots/dynamodb-table.png)

## Testing

```bash
curl -X POST https://<your-api-id>.execute-api.<region>.amazonaws.com/shorten \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://www.google.com\"}"
```

Response:
```json
{"shortId": "zssaLm", "shortUrl": "https://<your-api-id>.execute-api.<region>.amazonaws.com/zssaLm"}
```

Visiting the returned `shortUrl` in a browser redirects to the original URL.

## What I'd Change for Production

- Replace `AmazonDynamoDBFullAccess` with a scoped IAM policy limited to `GetItem`/`PutItem` on the specific table
- Add input validation (URL format checking) and rate limiting
- Add a TTL on DynamoDB items for expiring links
- Move infrastructure to Terraform for repeatable, version-controlled deployments
- Add CloudWatch alarms for error rates and Lambda throttling

## Cost

Both Lambda and DynamoDB (on-demand) are within the AWS Free Tier for low-traffic personal projects, so this costs effectively $0/month at small scale. API Gateway HTTP APIs also have a generous free tier.