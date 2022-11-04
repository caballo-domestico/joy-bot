import boto3
from boto3.dynamodb.conditions import Attr
from webserver.pub import Publisher, Topic
import logging

class PrescribedDrug:
    def __init__(self, name=None, frequency=None):
        self.name = name
        self.frequency = frequency

class PrescribedDrugsBean:
    def __init__(self, patientName=None, prescribedDrugs=None):
        self.patientName = patientName
        self.prescribedDrugs = prescribedDrugs

class FileBean:

    def __init__(self, file=None, key=None, bucketName=None, url=None):
        self.file = file   
        self.key = key      
        self.bucketName = bucketName    
        self.url = url  

class DynamoBean:
    def __init__(self, tableName=None, item=None, table=None):
        self.tableName = tableName
        self.item = item    # use it to store values in a table
        self.table = table  # the table corresponding with the requested tableName

class Dao:
    
    def __init__(self):
        self.s3Client = boto3.client('s3')
        self.dynamodbClient = boto3.client('dynamodb')
        self.dynamodb = boto3.resource('dynamodb')
    
    def makeS3ObjectUrl(self, bucketName, key):
        return f"https://{bucketName}.s3.amazonaws.com/{key}"
    
    def storeFileToS3(self, fileBean):
        self.s3Client.upload_fileobj(fileBean.file, fileBean.bucketName, fileBean.key)
        fileBean.url = self.makeS3ObjectUrl(fileBean.bucketName, fileBean.key)

    def loadFileFromS3(self, fileBean):
        self.s3Client.download_fileobj(fileBean.bucketName, fileBean.key, fileBean.file)

    def getTableFromDynamoDB(self, dynamoBean):
        dynamoBean.table = self.dynamodb.Table(dynamoBean.tableName)
    
    def storeToDynamoDB(self, dynamoBean):
        self.getTableFromDynamoDB(dynamoBean)
        dynamoBean.table.put_item(Item=dynamoBean.item)
    
class PrescriptionBean:

    def __init__(self, username=None, file=None, link=None, key=None, fileName=None):
        self.username = username
        self.file = file
        self.fileName = fileName
        self.link = link
        self.key = key

class PrescriptionsDao(Dao):

    def makeKey(self, ownername, filename):
        return f"{ownername}_{filename}"
    
    def __init__(self):
        super().__init__()
        self.tableName = "Prescriptions"
        self.bucketName = "joy-bot.prescriptions"
    
    def storePrescription(self, prescriptionBean):
        
        # stores prescription to s3
        key = self.makeKey(prescriptionBean.username, prescriptionBean.fileName)
        fileBean = FileBean(file=prescriptionBean.file, key=key, bucketName=self.bucketName)
        self.storeFileToS3(fileBean)

        # notify that a prescription has been uploaded
        p = Publisher()
        metadata=p.send(
            Topic.PRESCRIPTION_UPLOADED.value,
            value={
                "bucket" : fileBean.bucketName,
                "key" : fileBean.key,
                "s3link" : fileBean.url,
                "username": prescriptionBean.username,
            }).get(timeout=30)
        logging.debug(metadata)
        p.close()

        # stores prescrption metadata to dynamodb
        dynamoBean = DynamoBean(tableName=self.tableName, item={
            "id": key,
            "username": prescriptionBean.username,
            "fileName": prescriptionBean.file.filename,
            "link": fileBean.url
        })
        self.storeToDynamoDB(dynamoBean)

    def loadAllUserPrescriptionsNames(self, prescriptionBean):
        dynamoBean = DynamoBean(tableName=self.tableName, item={
            "username": prescriptionBean.username
        })
        self.getTableFromDynamoDB(dynamoBean)
        resultSet = dynamoBean.table.scan(
            Select="SPECIFIC_ATTRIBUTES",
            ProjectionExpression="fileName",
            FilterExpression=Attr("username").eq(prescriptionBean.username)
            )
        return [item["fileName"] for item in resultSet["Items"]]       

    def loadPrescription(self, prescriptionBean):
        key = self.makeKey(prescriptionBean.username, prescriptionBean.fileName)
        fileBean = FileBean(key=key, bucketName=self.bucketName, file=prescriptionBean.file)
        self.loadFileFromS3(fileBean)
