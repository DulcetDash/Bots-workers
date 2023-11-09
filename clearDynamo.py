import boto3

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                          aws_secret_access_key='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',
                          region_name='us-east-1')
table = dynamodb.Table('Catalogues')

def clear_dynamodb_table(table_name):
    # Initialize a DynamoDB client
    client = boto3.client('dynamodb')
    
    # Fetch all the items in the table
    response = table.scan()
    data = response.get('Items', [])
    
    # Continue fetching items if a LastEvaluatedKey was provided (indicates more data)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response.get('Items', []))

    # Delete each item individually
    with table.batch_writer() as batch:
        for item in data:
            print('Deleting item: {}'.format(item))
            batch.delete_item(
                Key={
                    'id': item['id'],
                    # Add other primary composite keys if your table uses them
                }
            )
    print('Table cleared!')

# Call the function to clear the table
clear_dynamodb_table('Catalogues')
