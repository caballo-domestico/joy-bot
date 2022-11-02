from email import message
import logging
from random import randint
import grpc
import boto3
from concurrent import futures
from dao import RegistrationDao, RegistrationBean
import time
import users_pb2_grpc as pb2_grpc
import users_pb2 as pb2


logging.basicConfig(level=logging.INFO)
class RegistrationService(pb2_grpc.RegistrationServicer):

    def __init__(self):
        pass
    
    def GetServerResponse(self, request, context):

        # get the string from the incoming request
        email = request.email
        password = request.password
        user_type = request.user_type
        phone_num = request.phone_num
        confirmed = request.confirmed

        registrationDao = RegistrationDao()
        registrationDao.registerUser(registrationBean=RegistrationBean(email=email, password=password, user_type=user_type, phone_num=phone_num, confirmed=confirmed))
        result = {'received': True}
        
        return pb2.MessageResponse(**result)    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_RegistrationServicer_to_server(RegistrationService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()