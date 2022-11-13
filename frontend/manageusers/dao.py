import boto3
from boto3.dynamodb.conditions import Attr
import logging
from pybreaker import CircuitBreaker
import config

class DynamoBean:
    def __init__(self, tableName=None, item=None, table=None, key=None, query=None):
        self.tableName = tableName
        self.item = item    # use it to store values in a table
        self.table = table  # the table corresponding with the requested tableName
        self.key = key      # key to get an item from table
        self.query = query

class Dao:
    
    circuitBreaker = CircuitBreaker(fail_max=config.CBREAKER_OPEN_AFTER, reset_timeout=config.CBREAKER_RESET_TIMEOUT)
    
    @circuitBreaker
    def __init__(self):
        self.dynamodbClient = boto3.client('dynamodb')
        self.dynamodb = boto3.resource('dynamodb')
    
    @circuitBreaker
    def getTableFromDynamoDB(self, dynamoBean):
        dynamoBean.table = self.dynamodb.Table(dynamoBean.tableName)
    
    @circuitBreaker
    def storeToDynamoDB(self, dynamoBean):
        self.getTableFromDynamoDB(dynamoBean)
        dynamoBean.table.put_item(Item=dynamoBean.item)
    
    @circuitBreaker
    def getItemFromTable(self, dynamoBean):
        item = self.dynamodbClient.get_item(TableName=dynamoBean.tableName, Key={dynamoBean.key:{'S':dynamoBean.query}})
        return item

    @circuitBreaker
    def deleteItemFromTable(self, dynamoBean):
        item = self.dynamodbClient.delete_item(TableName=dynamoBean.tableName, Key={dynamoBean.key:{'S':dynamoBean.query}})
        return item

    @circuitBreaker
    def updateItemFromTable(self, dynamoBean):
        table = self.dynamodb.Table(dynamoBean.tableName)
        response= table.update_item(
                Key={dynamoBean.key: dynamoBean.query},
                UpdateExpression="set confirmed=:c",
                ExpressionAttributeValues={
                    ':c': dynamoBean.item['confirmed']},
                ReturnValues="UPDATED_NEW")
        return response


class RegistrationBean:

    def __init__(self,email=None, password=None, username=None, phone_num=None, confirmed=None):
        self.email = email
        self.password = password
        self.username = username
        self.phone_num = phone_num
        self.confirmed = confirmed

class PinBean:

    def __init__(self,phone=None, pin=None):
        self.phone = phone
        self.pin = pin

class RegistrationDao(Dao):
    
    def __init__(self):
        super().__init__()
        self.tableName = "Users"
    
    def registerUser(self, registrationBean):
        dynamoBean = DynamoBean(tableName=self.tableName, item={
            "email": registrationBean.email,
            "password": registrationBean.password,
            "username": registrationBean.username,
            "phone_num": registrationBean.phone_num,
            "confirmed": registrationBean.confirmed
        })
        self.storeToDynamoDB(dynamoBean)

    def deleteUser(self, registrationBean):
        key_str = "phone_num"
        dynamoBean = DynamoBean(tableName=self.tableName, key=key_str, query=registrationBean.phone_num)
        self.deleteItemFromTable(dynamoBean)

    def updateUser(self, registrationBean):
        key_str = "phone_num"
        dynamoBean = DynamoBean(tableName=self.tableName, key=key_str, query=registrationBean.phone_num, item={
            'confirmed':True,
        })
        self.updateItemFromTable(dynamoBean)
    
    def getUser(self, registrationBean):
        key_str = "phone_num"
        dynamoBean = DynamoBean(tableName=self.tableName, key=key_str, query=registrationBean.phone_num)
        resp = self.getItemFromTable(dynamoBean)
        return resp


class PinDao(Dao):

    def __init__(self):
        super().__init__()
        self.tableName = "Pin"
    
    def registerPin(self, pinBean):
        dynamoBean = DynamoBean(tableName=self.tableName, item={
            "phone": pinBean.phone,
            "pin": pinBean.pin,
        })
        self.storeToDynamoDB(dynamoBean)
    
    def getPin(self, pinBean):
        key_str = "phone"
        dynamoBean = DynamoBean(tableName=self.tableName, key=key_str, query=pinBean.phone)
        pin = self.getItemFromTable(dynamoBean)
        return pin

    def deletePin(self, pinBean):
        key_str = "phone"
        dynamoBean = DynamoBean(tableName=self.tableName, key=key_str, query=pinBean.phone)
        self.deleteItemFromTable(dynamoBean)
