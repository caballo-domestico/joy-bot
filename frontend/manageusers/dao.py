import boto3
from boto3.dynamodb.conditions import Attr

class DynamoBean:
    def __init__(self, tableName=None, item=None, table=None):
        self.tableName = tableName
        self.item = item    # use it to store values in a table
        self.table = table  # the table corresponding with the requested tableName

class Dao:
    
    def __init__(self):
        self.dynamodbClient = boto3.client('dynamodb')
        self.dynamodb = boto3.resource('dynamodb')
    
    def getTableFromDynamoDB(self, dynamoBean):
        dynamoBean.table = self.dynamodb.Table(dynamoBean.tableName)
    
    def storeToDynamoDB(self, dynamoBean):
        self.getTableFromDynamoDB(dynamoBean)
        dynamoBean.table.put_item(Item=dynamoBean.item)
    
class RegistrationBean:

    def __init__(self,email=None, password=None, user_type=None):
        self.email = email
        self.password = password
        self.user_type = user_type

class RegistrationDao(Dao):
    
    def __init__(self):
        super().__init__()
        self.tableName = "Users"
    
    def registerUser(self, registrationBean):
        dynamoBean = DynamoBean(tableName=self.tableName, item={
            "email": registrationBean.email,
            "password": registrationBean.password,
            "user_type": registrationBean.user_type
        })
        self.storeToDynamoDB(dynamoBean)