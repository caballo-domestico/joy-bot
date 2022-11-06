import grpc
import users_pb2_grpc
import users_pb2

class Client:

    def __init__(self, host, server_port):

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(host, server_port))


class RegistrationClient(Client):
    """
    Client for gRPC functionality
    """

    def __init__(self, host, port):
        super().__init__(host, port)

        # bind the client and the server
        self.stub = users_pb2_grpc.RegistrationStub(self.channel)

    def get_user(self, email, password, user_type, phone_num, confirmed):
        message = users_pb2.Message(email=email, password=password, user_type=user_type, phone_num=phone_num, confirmed=confirmed)
        print(f'{message}')
        return self.stub.GetServerResponse(message)

