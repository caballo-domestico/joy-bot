import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('analisi')

table.put_item(
   Item={
        'cf': 'provacf',
        'tipologia': 'radiografia',
        'nome': 'Daniele' 
    }
)

key = "cf"
response = table.get_item(
   Key={
        'cf': key
    }
)

print(response)