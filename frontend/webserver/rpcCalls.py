import grpc
import users_pb2_grpc
import users_pb2
import prescription_analyzer_pb2
import prescription_analyzer_pb2_grpc
from pybreaker import CircuitBreaker

CBREAKER_OPEN_AFTER=1
CBREAKER_RESET_TIMEOUT=30


class Client:

    def __init__(self, host, server_port):

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(host, server_port))


class RegistrationClient(Client):
    """
    Client for gRPC functionality
    """
    circuitBreaker = CircuitBreaker(fail_max=CBREAKER_OPEN_AFTER, reset_timeout=CBREAKER_RESET_TIMEOUT)
    
    @circuitBreaker
    def __init__(self, host, port):
        super().__init__(host, port)

        # bind the client and the server
        self.stub = users_pb2_grpc.RegistrationStub(self.channel)
    @circuitBreaker
    def get_user(self, email, password, username, phone_num, confirmed):
        message = users_pb2.Message(email=email, password=password, username=username, phone_num=phone_num, confirmed=confirmed)
        print(f'{message}')
        return self.stub.UsersRegistration(message)
    
    @circuitBreaker
    def manage_pin(self, phone, db_op, real_user, pin=0):
        message = users_pb2.PinMessage(phone=phone, pin=pin, db_op=db_op, real_user=real_user)
        return self.stub.PinRegistration(message)
    
    @circuitBreaker
    def log_user(self, phone_num):
        message = users_pb2.LoginMessage(phone_num=phone_num)
        return self.stub.Login(message)

class PrescribedDrugsDao(Client):
    circuitBreaker = CircuitBreaker(fail_max=CBREAKER_OPEN_AFTER, reset_timeout=CBREAKER_RESET_TIMEOUT)

    @circuitBreaker
    def __init__(self, host, port):
        super().__init__(host, port)

        # bind the client and the server
        self.stub = prescription_analyzer_pb2_grpc.PrescriptionAnalyzerStub(self.channel)
    @circuitBreaker
    def getPrescribedDrugs(self, username):
        """
        Returns an iterator of prescribed drugs for a given username
        """
        
        message = prescription_analyzer_pb2.PatientUsername(username=username)
        return self.stub.getPrescribedDrugs(message)