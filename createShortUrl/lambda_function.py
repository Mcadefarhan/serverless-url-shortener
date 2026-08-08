import json
import boto3
import string
import random

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UrlShortener')

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        long_url = body.get('url')

        if not long_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing "url" in request body'})
            }

        short_id = generate_short_id()

        table.put_item(
            Item={
                'shortId': short_id,
                'longUrl': long_url
            }
        )

        api_id = event['requestContext']['apiId']
        region = 'ap-southeast-2'
        short_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{short_id}"

        return {
            'statusCode': 200,
            'body': json.dumps({
                'shortId': short_id,
                'shortUrl': short_url
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }