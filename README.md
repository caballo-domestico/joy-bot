# joy-bot

❤️ Your distributed sweet caretaker ❤️

JoyBot is a web service able to assist you with your medical everyday TODOs. All you have to do is to upload an image or a PDF of your medical prescriptions. JoyBot will analyze the uploaded prescriptions and will remind you of what drugs you have to take, along with their frequency.

## Deploy in an AWS EC2 instance

The entire application can be deployed in a remote AWS ec2 instance using the `deploy.sh` script:
```
$ cd deploy
$ ./deploy.sh
Usage: ./deploy.sh path/to/ssh/key.pem [--skip-terraform]  [--skip-dependencies]
```
The above mentioned script will perform the following steps:
- Create the required infrastructure from Amazon Web Services using Terraform;
- Compile the proto files to sources using Make;
- Write a `hosts` text file with the informations needed to ssh to the remote EC2 instance;
- Install docker and app files and launch it using Ansible.

Each step executes only if actual changes are detected (i.e. changes in sources, a container goes down, ...)

During Terraform step, you will be prompted to enter the name of an existing AWS key pair to use to ssh to the instance. You can also specify the name of a bucket to store prescription. If the bucket does not exists, it will be created.

During Ansible step, when asked for BECOME password, insert your ec2-user sudo password. If you do not use a password when invoking sudo as ec2-user, simply hit `Enter` key.

## Configuration

All microservices configuration parameters are speciied as command line args. You can see the dockerfile of each microservice to see what parameters you can tune.

To tune the infrastructure parameters you can peek at the terraform scripts in the `demiurges` folder.

By default, JoyBot will listen for HTTP request behind port 8080 of host. You can change it in the `frontend/docker-compose.yml` file.

JoyBot needs valid AWS credentials files to work. By default, when the containers are built a volume is mounted taking files from `~/.aws` host folder. You can change it in the `frontend/docker-compose.yml` file if you put your AWS credentials and config in another place.

## Execution in local machine

If you deployed the app in a local machine, run the following commands to build and launch the app:
```
$ cd frontend
$ ./start-orchestration.sh
```

You must have installed `docker-compose`, `protoc` and the Python and Go plugins of it.

## Execution in remote AWS EC2 instance

If you deployed the app using `deploy.sh` the app was already launched for you by Ansible.

If you deployed the app using other means, you must ssh to the ec2 and follow steps in [Execution in local machine](README.md#execution-in-local-machine)
