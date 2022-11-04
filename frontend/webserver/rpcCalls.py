import grpc
import users_pb2_grpc as pb2_grpc
import users_pb2 as pb2

class RegistrationClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self):
        self.host = 'signin'
        self.server_port = 50051

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client and the server
        self.stub = pb2_grpc.RegistrationStub(self.channel)

    def get_user(self, email, password, user_type, phone_num, confirmed):
        message = pb2.Message(email=email, password=password, user_type=user_type, phone_num=phone_num, confirmed=confirmed)
        print(f'{message}')
        return self.stub.GetServerResponse(message)