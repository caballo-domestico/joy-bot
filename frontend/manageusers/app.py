from email import message
import logging
from random import randint
import grpc
import boto3
from concurrent import futures
from dao import RegistrationDao, RegistrationBean, PinBean, PinDao
import time
import users_pb2_grpc as pb2_grpc
import users_pb2 as pb2
import argparse
import config

logging.basicConfig(level=logging.INFO)
class RegistrationService(pb2_grpc.RegistrationServicer):

    def __init__(self):
        pass
    
    def UsersRegistration(self, request, context):

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
    
    def PinRegistration(self, request, context):

        phone = request.phone
        pin = request.pin
        db_op = request.db_op
        real_user = request.real_user

        pinDao = PinDao()
        if db_op == "add":
            pinDao.registerPin(pinBean=PinBean(phone=phone, pin=pin))
            return pb2.PinMessageResponse(received=True, pin=0)

        elif db_op == "get":
            resp = pinDao.getPin(pinBean=PinBean(phone=phone))
            pin= resp['Item']['pin']['N']
            return pb2.PinMessageResponse(received=True, pin=int(pin))

        elif db_op == "rm":
            registrationDao = RegistrationDao()
            pinDao.deletePin(pinBean=PinBean(phone=phone))
            if not real_user:
                registrationDao.deleteUser(registrationBean=RegistrationBean(phone_num=phone))
            else:
                registrationDao.updateUser(registrationBean=RegistrationBean(phone_num=phone, confirmed=True))
            return pb2.PinMessageResponse(received=True, pin=0)
        
    def Login(self, request, context):
        phone = request.phone_num
        registrationDao = RegistrationDao()
        response = registrationDao.getUser(registrationBean=RegistrationBean(phone_num=phone))
        if 'Item' in response:
            return pb2.LoginResponse(password=response['Item']['password']['S'], confirmed=response['Item']['confirmed']['BOOL'])
        return pb2.LoginResponse(password='not found', confirmed=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_RegistrationServicer_to_server(RegistrationService(), server)
    server.add_insecure_port(config.GRPC_ADDR_PORT)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--grpc_addr_port', default=config.GRPC_ADDR_PORT, help='addr:portNum for receive grpc requests')
    parser.add_argument("--cbreaker_open_after", default=config.CBREAKER_OPEN_AFTER, type=int, help="how many failures before circuit breaker opens")
    parser.add_argument("--cbreaker_reset_timeout", default=config.CBREAKER_RESET_TIMEOUT, type=int, help="how many seconds before circuit breaker closes again")
    args = parser.parse_args()

    config.GRPC_ADDR_PORT = args.grpc_addr_port
    config.CBREAKER_OPEN_AFTER = args.cbreaker_open_after
    config.CBREAKER_RESET_TIMEOUT = args.cbreaker_reset_timeout

    serve()