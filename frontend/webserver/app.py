from crypt import methods
import email
from flask import Flask, render_template, request, flash, send_file, redirect, make_response
import os
from werkzeug.utils import secure_filename
from random import randint
import botocore
import boto3
from botocore.config import Config
from rpcCalls import RegistrationClient, PrescribedDrugsDao
from dao import PrescriptionsDao, PrescriptionBean
from tempfile import TemporaryFile
from urllib.parse import quote_plus
from flask_bootstrap import Bootstrap5
import logging
import argparse
import pub
import config

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.urandom(24).hex()
ALLOWED_EXTENSIONS = {'pdf', "png", "jpg", "jpeg"}

def user_cookie(dict, page, age=None):
    resp = make_response(redirect(page))
    for i in dict:
        resp.set_cookie(i, dict[i], max_age=age)
    return resp 

def check_auth():
    return request.cookies.get('logged')

def isLogged():
    if  check_auth() is not None and check_auth() == 'true':
        return True
    return False

def redirectToLogin():
    flash('Login needed for this operation', category="danger")
    return redirect('loginuser')

def enforceLogin(func):
    def _login(*args, **kwargs):
        if not isLogged():
            return redirectToLogin()
        else:
            return func(*args, **kwargs)
    _login.__name__ = func.__name__
    return _login

@app.context_processor
def inject_isLogged():
    return dict(isLogged=isLogged)

@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template(template_name_or_list='home.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/signin', methods=('GET', 'POST'))
def signin():
    auth = 'auth'
    if request.method == 'POST':
        email = request.form.get("umail")
        password = request.form.get("upass")
        username = request.form.get("username")
        phone_num = request.form.get("uprefix")+request.form.get("uphone")
        rpc_obj = RegistrationClient(host=config.GRPC_MANAGEUSER_ADDR, port=config.GRPC_MANAGEUSER_PORT)
        response = rpc_obj.get_user(email=email, password=password, username=username, phone_num=phone_num, confirmed=False)
        if response.available:
            cookies = {
                'userphone':phone_num, 
                'username':username,
                'count':'1'
            }
            resp = user_cookie(dict=cookies, page=auth)
            sms_sender(phone_num)
            return resp
        elif not response.available:
            flash('Unavailable username', category="danger")
        elif  not response.unregistered:
            flash("Phone number already exists", category="danger")
    return render_template('signin.html')

@app.route('/auth', methods=('GET', 'POST'))
def confirmation():
    rpc_obj = RegistrationClient(host=config.GRPC_MANAGEUSER_ADDR, port=config.GRPC_MANAGEUSER_PORT)

    if request.method == 'POST':
        op = 'get'
        pin = request.form.get("upin")
        phone_num = request.cookies.get('userphone')
        response = rpc_obj.manage_pin(phone=phone_num, db_op=op, real_user=False)
        db_pin = response.pin

        if(request.cookies.get('count')>='3'):
            op="rm"
            rpc_obj.manage_pin(phone=phone_num, db_op=op, real_user=False)
            flash('Espired pin, insert your data again', category="danger")
            return render_template('signin.html')

        elif(str(pin) == str(db_pin)):
            op = "rm"
            page='loginuser'
            counter = {
                'count': '0'
            }     
            rpc_obj.manage_pin(phone=phone_num, db_op=op, real_user=True)
            ret = user_cookie(dict=counter, page=page, age=0)
            return ret
        else:
            page = 'auth' 
            value = int(request.cookies.get('count'))+1
            counter = {
                'count': str(value)
            }     
            ret = user_cookie(dict=counter, page=page)
            flash(f'Wrong pin, {str(4-value)} try left', category="danger")
            return ret
    return render_template('auth.html')

@app.route('/loginuser', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        rpc_obj = RegistrationClient(host=config.GRPC_MANAGEUSER_ADDR, port=config.GRPC_MANAGEUSER_PORT)
        phone_num = request.form.get('uprefix')+request.form.get('uphone')
        response = rpc_obj.log_user(phone_num)
        if response.password=='not found':
            flash('Wrong username or password', category="danger")
            return render_template('loginuser.html')
        db_pass = response.password
        confirmed = response.confirmed
        if(db_pass == request.form.get('upass') and confirmed):
            cookie_dict = {'logged':'true',
                        'userphone':phone_num,
                        'username':response.username}
            page = '/'
            resp = user_cookie(cookie_dict, page)
            return resp 
        elif not confirmed:
            return render_template('auth.html')
        else:
            return render_template('loginuser.html')
    return render_template('loginuser.html')

@app.route('/home', methods=['GET'])
def logout():
    cookie_dict = {'logged':'false'}
    page = 'loginuser'
    ret = user_cookie(dict=cookie_dict, page=page)
    return ret

def sms_sender(phone_num):
    logging.info('SENDING SMS')
    sns = boto3.resource("sns")
    op = 'add'
    pin = randint(100000, 999999)
    message = "This is your account verification pin:{}".format(pin) 
    sns.meta.client.publish(PhoneNumber=phone_num, Message=message)
    rpc_obj = RegistrationClient(host=config.GRPC_MANAGEUSER_ADDR, port=config.GRPC_MANAGEUSER_PORT)
    try:
        ret_sms=sns.meta.client.publish(PhoneNumber=phone_num, Message=message)
        logging.info("Published message to %s.", phone_num)
        logging.info("RETURN %s", ret_sms)
        rpc_obj.manage_pin(phone=phone_num, pin=pin, db_op=op, real_user=False)

    except botocore.exceptions.ClientError:
        logging.exception("Couldn't publish message to %s.", phone_num)
        raise
    else:
        return pin

@app.route('/upload-prescription', methods=('GET', 'POST'))
@enforceLogin
def upload_prescription():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'prescription' not in request.files:
            flash('No prescription selected', "danger")
        file = request.files['prescription']
        if file.filename == '':
            flash('No selected file', "danger")
        if file and not allowed_file(file.filename):
            flash(f'file types allowed: {ALLOWED_EXTENSIONS}', "danger")
        if file and allowed_file(file.filename):
            
            # uploads prescription and its metadata to db
            filename = secure_filename(file.filename).replace(" ", "_")
            username=quote_plus(request.cookies.get('username'))
            dao = PrescriptionsDao()
            bean = PrescriptionBean(username=username, file=file, fileName=filename)
            dao.storePrescription(prescriptionBean=bean)

            return redirect(f"/list-prescriptions?username={username}")
    return render_template('upload-prescription.html')

@app.route('/list-prescriptions', methods=['GET'])
@enforceLogin
def list_prescriptions():
    logged = check_auth()
    if not isLogged():
        redirectToLogin()

    username = request.args.get('username', type=str)
    dao = PrescriptionsDao()
    names = dao.loadAllUserPrescriptionsNames(prescriptionBean=PrescriptionBean(username=username))
    logging.info('Names %s', names)
    return render_template('list-prescriptions.html', names=names, username=username)

@app.route('/get-prescription', methods=['GET'])
@enforceLogin
def get_prescription():
    logged = check_auth()
    if logged == 'false':
        flash('Login needed for this operation')
        return render_template('loginuser.html')
    dao = PrescriptionsDao()
    fileName = request.args.get('fileName', type=str)
    username = request.args.get('username', type=str)
    buf = TemporaryFile(mode="w+b")
    logging.info('Filename %s', fileName+' '+username)
    prescriptionBean = PrescriptionBean(username=username, file=buf, fileName=fileName)
    dao.loadPrescription(prescriptionBean=prescriptionBean)
    buf.seek(0)
    response = send_file(buf, download_name=fileName, as_attachment=True)
    return response

@app.route('/dashboard', methods=['GET'])
@enforceLogin
def dashboard():
    username = request.args.get('username', type=str)
    dao = PrescribedDrugsDao(config.GRPC_PANALYZER_ADDR, config.GRPC_PANALYZER_PORT)
    prescribedDrugs = dao.getPrescribedDrugs(username)
    return render_template('dashboard.html', prescribedDrugs=prescribedDrugs, username=username)
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kafka_port",
        default="9092",
        help="Port of the Kafka server.",
        type=int,
        )
    parser.add_argument(
        "--kafka_addr",
        default="kafka",
        help="Address of the Kafka server.",
        )
    parser.add_argument(
        "--grpc_panalyzer_addr",
        default=config.GRPC_PANALYZER_ADDR,
        help="Address of the prescription analyzer gRPC server.",
        )
    parser.add_argument(
        "--grpc_panalyzer_port",
        default=config.GRPC_PANALYZER_PORT,
        help="port of the prescription analyzer gRPC server",
        type=int,
        )
    parser.add_argument(
        "--grpc_manageuser_addr",
        default=config.GRPC_MANAGEUSER_ADDR,
        help="Address of the manage user gRPC server.",
        )
    parser.add_argument(
        "--grpc_manageuser_port",
        default=config.GRPC_MANAGEUSER_PORT,
        help="port of the manage user gRPC server",
        type=int,
        )
    parser.add_argument(
        "--host_addr",
        default=config.HOST_ADDR,
        help="Address of this webserver.",
        )
    parser.add_argument(
        "--host_port",
        default=config.HOST_PORT,
        help="Port of this webserver.",
        type=int,
        )
    parser.add_argument(
        "--bucket_prescriptions",
        default=config.BUCKET_PRESCRIPTIONS,
        help="name of the bucket where to store prescriptions",
        )
    args = parser.parse_args()

    config.HOST_ADDR = args.host_addr
    config.HOST_PORT = args.host_port
    config.GRPC_MANAGEUSER_ADDR = args.grpc_manageuser_addr
    config.GRPC_MANAGEUSER_PORT = args.grpc_manageuser_port
    config.GRPC_PANALYZER_ADDR = args.grpc_panalyzer_addr
    config.GRPC_PANALYZER_PORT = args.grpc_panalyzer_port
    config.BUCKET_PRESCRIPTIONS = args.bucket_prescriptions

    pub.setKafkaAddr(addr=args.kafka_addr, port=args.kafka_port)

    app.run(debug=True, host=config.HOST_ADDR)
