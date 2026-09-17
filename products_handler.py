import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('products')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    
    if http_method == 'POST':
        return create_product(event)
    elif http_method == 'GET':
        if event.get('pathParameters'):
            return get_product(event)
        return get_all_products()
    elif http_method == 'PUT':
        return update_product(event)
    elif http_method == 'DELETE':
        return delete_product(event)

def create_product(event):
    body = json.loads(event['body'])
    product = {
        'product_id': str(uuid.uuid4()),
        'name': body['name'],
        'price': body['price'],
        'description': body.get('description', ''),
        'stock': body.get('stock', 0),
        'created_at': datetime.utcnow().isoformat()
    }
    table.put_item(Item=product)
    return response(201, product)

def get_product(event):
    product_id = event['pathParameters']['product_id']
    result = table.get_item(Key={'product_id': product_id})
    item = result.get('Item')
    if not item:
        return response(404, {'message': 'Product not found'})
    return response(200, item)

def get_all_products():
    result = table.scan()
    return response(200, result['Items'])

def update_product(event):
    product_id = event['pathParameters']['product_id']
    body = json.loads(event['body'])
    table.update_item(
        Key={'product_id': product_id},
        UpdateExpression='SET #n = :n, price = :p, stock = :s',
        ExpressionAttributeNames={'#n': 'name'},
        ExpressionAttributeValues={
            ':n': body['name'],
            ':p': body['price'],
            ':s': body.get('stock', 0)
        }
    )
    return response(200, {'message': 'Product updated!'})

def delete_product(event):
    product_id = event['pathParameters']['product_id']
    table.delete_item(Key={'product_id': product_id})
    return response(200, {'message': 'Product deleted!'})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, default=str)
    }
