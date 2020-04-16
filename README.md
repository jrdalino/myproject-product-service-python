# myproject-product-service-python

## Functional Requirements
- Create, Read, Update, Delete, and List Products

## API Endpoints
```
| HTTP METHOD | URI                                      | ACTION                       |
|-------------|------------------------------------------|------------------------------|
| GET         | http://[hostname]/products              | Gets all products           |
| GET         | http://[hostname]/products/<productId> | Gets one product            |
| POST        | http://[hostname]/products              | Creates a new product       |
| PUT         | http://[hostname]/products/<productId> | Updates an existing product |
| DELETE      | http://[hostname]/products/<productId> | Deletes a product           |
```

## Prerequisites
- Docker, Python, Flask, Git, Virtualenv https://github.com/jrdalino/development-environment-setup
- Setup CI/CD using https://github.com/jrdalino/myproject-aws-codepipeline-product-service-terraform. This will create CodeCommit Repo, ECR Repo, CodeBuild Project, Lambda Function and CodePipeline Pipeline 
- Create ELB Service Role if it doesnt exist yet
```
$ aws iam get-role --role-name "AWSServiceRoleForElasticLoadBalancing" || aws iam create-service-linked-role --aws-service-name "elasticloadbalancing.amazonaws.com"
```

## Structure and Environment
- Clone CodeCommit Repository and navigate to working directory
```bash
$ cd ~/environment
$ git clone https://git-codecommit.ap-southeast-2.amazonaws.com/v1/repos/myproject-product-service && cd ~/environment/myproject-product-service
```

- Follow folder structure as per https://flask.palletsprojects.com/en/1.1.x/tutorial/layout/
```
$ ~/environment/myproject-product-service
├── flaskr/
│   ├── __init__.py
│   ├── app.py
│   ├── custom_logger.py
│   ├── db.py
│   ├── product_routes.py
│   ├── product_table_client.py
│   └── requirements.txt
├── kubernetes/
│   ├── deployment.yml
│   └── service.yml
├── tests/
│   ├── __init__.py
│   ├── products.json
│   ├── test_curl.sh
│   ├── test_product_routes.py
│   ├── test_db.py
│   └── test_factory.py
├── venv/
├── .gitignore
├── buildspec.yml
├── Dockerfile
└── README.md
```

- Activate virtual environment before installing flask, flask-cors and boto3
```bash
$ cd ~/environment/myproject-product-service/myproject-product-service
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ venv/bin/pip install flask flask-cors boto3 aws-xray-sdk
(venv) $ deactivate # To deactivate
```

## Logging
- Add custom logger ~/environment/myproject-product-service/flaskr/custom_logger.py

## Local Development
- Setup Local DynamoDB
```
$ docker pull amazon/dynamodb-local
$ docker run -p 8000:8000 amazon/dynamodb-local
```
- Create Local DynamoDB Table
```
$ aws dynamodb create-table \
--cli-input-json file://~/environment/products-table-schema.json \
--endpoint-url http://localhost:8000 
```
```
{
  "TableName": "products",
  "ProvisionedThroughput": {
    "ReadCapacityUnits": 5,
    "WriteCapacityUnits": 5
  },
  "AttributeDefinitions": [
    {
      "AttributeName": "productId",
      "AttributeType": "S"
    }
  ],
  "KeySchema": [
    {
      "AttributeName": "productId",
      "KeyType": "HASH"
    }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "name_index",
      "KeySchema": [
        {
          "AttributeName": "productId",
          "KeyType": "HASH"
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      },
      "ProvisionedThroughput": {
        "ReadCapacityUnits": 5,
        "WriteCapacityUnits": 5
      }
    }
  ]
}
```

## Development
- You may also copy everything from Github repo to CodeCommit repo
```
$ rsync -rv --exclude=.git ~/environment/myproject-product-service-python/ ~/environment/myproject-product-service/
```
OR
- Add application factory               ~/environment/myproject-product-service/flaskr/__init__.py
- Create the dynamodb table using       https://github.com/jrdalino/myproject-aws-dynamodb-product-service-terraform
- Add static database                   ~/environment/myproject-product-service/tests/products.json
- Connect to the database               ~/environment/myproject-product-service/flaskr/db.py

- Add product dynamodb table client    ~/environment/myproject-product-service/flaskr/product_table_client.py
- Add product routes                   ~/environment/myproject-product-service/flaskr/product_routes.py
- Add app                               ~/environment/myproject-product-service/flaskr/app.py


## Run
- Run locally
```bash
$ cd flaskr
$ python app.py
$ curl http://localhost:5000
```

## Testing
- Add tests using curl ~/environment/myproject-product-service/tests/test_curl.sh
- Replace hostname and port variables
- Run tests using curl
```
$ cd ~/environment/myproject-product-service/tests
$ chmod a+x test_curl.sh
$ ./test_curl.sh
```
- Install pytest and coverage to test and measure your code, pytest-flask and moto to mock your flask server and mock dynamodb 
```
(venv) $ venv/bin/pip install pytest coverage pytest-flask moto
```
- Add static database ~/environment/myproject-product-service/tests/products.json
- Add tests for factory ~/environment/myproject-product-service/tests/test_factory.py
- Add tests for database ~/environment/myproject-product-service/tests/test_db.py
- Add ~/environment/myproject-product-service/tests/__init__.py
- Add tests for product routes ~/environment/myproject-product-service/tests/test_product_routes.py
- Run tests and measure code coverage
```
$ pytest
$ coverage run -m pytest
$ coverage report
$ coverage html # open htmlcov/index.html in a browser
```
- TODO: Add tests for other AWS Services https://github.com/spulec/moto

## Containerize
- Generate ~/environment/myproject-product-service/flaskr/requirements.txt
```bash
$ pip freeze > requirements.txt
```
- Add Docker File ~/environment/myproject-product-service/Dockerfile
- Build, Tag and Run the Docker Image locally. (Replace AccountId and Region)
```bash
$ cd ~/environment/myproject-product-service
$ docker build -t myproject-product-service .
$ docker tag myproject-product-service:latest 222337787619.dkr.ecr.ap-southeast-2.amazonaws.com/myproject-product-service:latest
$ docker run -e AWS_ACCESS_KEY_ID=<REPLACE_ME> -e AWS_SECRET_ACCESS_KEY=<REPLACE_ME> -d -p 5000:5000 myproject-product-service:latest
$ curl http://localhost:5000
```
- Note: For manual deployment only, create the image repositories manually
```bash
$ aws ecr create-repository --repository-name myproject-product-service
```
- Push Docker Image to ECR and validate
```bash
$ $(aws ecr get-login --no-include-email)
$ docker push 222337787619.dkr.ecr.ap-southeast-2.amazonaws.com/myproject-product-service:latest
$ aws ecr describe-images --repository-name myproject-product-service
```

## Run and Test Locally
```
$ docker-compose up
```
```
version: '3'
services:
  # https://github.com/aws-samples/aws-sam-java-rest/issues/1
  dynamo-db:
    image: amazon/dynamodb-local
    ports:
      - '8000:8000'
    volumes:
      - dynamodb_data:/home/dynamodblocal
    working_dir: /home/dynamodblocal
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ."

  api:
    build: .
    volumes:
      - ./flaskr:/flaskr
    ports:
      - '5000:5000'
    links: 
      - dynamo-db
volumes:
  dynamodb_data:
```

## Change Database to DynamoDB on AWS

## Pre-Deployment
- Add .gitignore file ~/environment/myproject-product-service/.gitignore
- Add Kubernetes Deployment and Service Yaml files ~/environment/myproject-product-service/kubernetes/deployment.yml and ~/environment/myproject-product-service/kubernetes/service.yml

## Manual Deployment
- Create k8s Deployment and Service
```
$ cd ~/environment/myproject-product-service/kubernetes
$ kubectl apply -f deployment.yml
$ kubectl apply -f service.yml
$ kubectl get all
```

## Automated Deployment
- Review https://github.com/jrdalino/myproject-aws-codepipeline-product-service-terraform
- Add Buildspec Yaml file ~/environment/myproject-product-service/buildspec.yml
- Make changes, commit and push changes to CodeCommit repository to trigger codepipeline deployment to EKS
```bash
$ git add .
$ git commit -m "Initial Commit"
$ git push origin master
```
- Create k8s Service (You only have to do this once)
```
$ cd ~/environment/myproject-product-service/kubernetes
$ kubectl apply -f service.yml
$ kubectl get all
```

## (Optional) Clean up
```bash
$ kubectl delete -f service.yml
$ kubectl delete -f deployment.yml
$ aws ecr delete-repository --repository-name myproject-product-service --force
$ aws codecommit delete-repository --repository-name myproject-product-service
$ rm -rf ~/environment/myproject-product-service
$ docker ps
$ docker kill <CONTAINER_ID>
$ docker images
$ docker system prune -a
```