import grpc
from concurrent import futures
from manageusers.dao import RegistrationDao, RegistrationBean
import time
import manageusers.users_pb2_grpc as pb2_grpc
import manageusers.users_pb2 as pb2


class RegistrationService(pb2_grpc.RegistrationServicer):

    def __init__(self, *args, **kwargs):
        pass

    def GetServerResponse(self, request, context):

        # get the string from the incoming request
        email = request.email
        password = request.password
        user_type = request.user_type

        registrationDao = RegistrationDao()
        registrationDao.registerUser(registrationBean=RegistrationBean(email=email, password=password, user_type=user_type))
        result = {'received': True}

        return pb2.MessageResponse(**result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_RegistratioServicer_to_server(RegistrationService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()