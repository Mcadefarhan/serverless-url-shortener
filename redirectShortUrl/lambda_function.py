import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UrlShortener')

def lambda_handler(event, context):
    try:
        short_id = event['pathParameters']['shortId']

        response = table.get_item(Key={'shortId': short_id})
        item = response.get('Item')

        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Short URL not found'})
            }

        long_url = item['longUrl']

        return {
            'statusCode': 301,
            'headers': {
                'Location': long_url
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }