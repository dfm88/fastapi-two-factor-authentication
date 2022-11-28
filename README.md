## Contents
- [Intro](#intro)
- [Flowchart](#flowchart)
- [Models](#models)
  - [User](#user) 
  - [Device](#device)
  - [Backup Tokens](#backup-tokens)
- [Endpoints](#endpoints)
  - [Auth](#auth)
  - [Two Factor Authentication](#two-factor-authentication)
  - [Users](#users)
  - [Tasks](#tasks)
- [Crud](#crud)
- [Core](#core)
## Run
- [Run from docker-compose](#run-from-docker-compose)

## Todo
- [Todos](#todos)


__________
__________
### **[Intro](#intro)**
The application is an authentication microservice, developed with FastAPI framework, for login access via JWT token and possibility to enable two factor authentication (TFA).

**Two Factor Authentication**

TFA can be enabled choosing by two kind of devices:
* email (OTP token will be send via email)
* code generator (on activation a qr code is send to the user that, since than, will have the OTP token in any authenticator app like Microsoft or Google Authenticator apps)

It is only available the TOTP version of OTP validation protocol, based on timestamp and a private key for each user.

**Backup Tokens**

On TFA activation, independently from the chosen device, an email will be sent to the user with 5 backup tokens that can be used in case qr code was lost or it's somehow not possible to receive the token, these backup tokens are consumed every time one is used.

**Email service**

Email sending is faked by printing on stout the sent email text. It is anyway handled by a Celery consumer listening on a RabbitMQ message broker.

**Services**

The app run inside Docker, orchestrated by docker-compose. Database is Postgres, RabbitMq is used as message broker for Celery tasks and Redis is used as a backend for saving tasks results. It is also available a Flower instance to check task status via web dashboard.

|  service | container name  | listening port |
|---|---|---|
| **FastAPI**  | fastapi_2fa  | 5555  |
| **PostgresDB**  | fastapi_2fa-db  | 5454  |
| **Redis**  | fastapi_2fa-cache  | 6389  |
| **RabbitMQ**  | fastapi_2fa-rabbitmq  | 15672  |
| **Celery worker**  | fastapi_2fa-celery  |   |
| **Flower**  | fastapi_2fa-flower  | 5557  |




### **[Flowchart](#flowchart)**

<img src="https://raw.githubusercontent.com/dfm88/fastapi-two-factor-authentication/main/docs/two_factor_flowchart.drawio.png" alt="image" style="width:600px;"/>


### **[Models](#models)**

User model has a One to One relationship with Device model. Device model has a One to Many relationship with BackupTokens model.

#### [User](#user)
    
* `full_name` - user name 
* `email` - used for login
* `hashed_password` - user hashed password
* `tfa_enabled` - boolean field to determine if user has TFA enabled

#### [Device](#device)
    
* `user_id` - associated user 
* `key` - here is saved the encrypted version of the user OTP key
* `device_type` - string value to determine if TFA device is of type `email` or `code_generator`

#### [Backup Tokens](#backup-tokens)
    
* `device_id` - associated device 
* `token` - random TOTP backup token

### **[Endpoints](#endpoints)**

Endpoints can be easily tested via FastAPI Swagger on route `/docs`. here are proposed the `curl` version to easily set JWT tokens

#### [Auth](#auth)

* `/api/v1/auth/signup`

    **POST** - Creates a new user. 
    
    `device` key is required only if `tfa_enabled` is `true`; 
    
    `device_type` is one between `email` or `code_generator`

    **body**

    ```json
    {
        "email": "user@example.com",
        "tfa_enabled": true,
        "full_name": "string",
        "password": "123456",
        "device": {
            "device_type": "email"
        }
    }
    ```
    
    **curl** (the `--output` option will save on your filesystem a valid qr-code image only if device type is `code_generator`)

    ```shell
    curl -X 'POST' \
    'http://localhost:5555/api/v1/auth/signup' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "email": "user@example.com",
    "tfa_enabled": true,
    "full_name": "string",
    "password": "123456",
    "device": {
        "device_type": "email"
    }
    }' --output my_qrcode.png
    ```

* `/api/v1/auth/login`

    **POST** - Authenticates new user

    **form data**

    ```
    Email
    Password
    ```
    
    **curl**

    ```shell
    curl -X 'POST' \
    'http://localhost:5555/api/v1/auth/login' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=&username={{ USERNAME }}&password={{ PASSWORD }}&scope=&client_id=&client_secret='
    ```

* `/api/v1/auth/test-token`

    **GET** - Test authenticated endpoint to check if user is authenticated, JWT token must be set in `Authorization` header
    
    **curl**

    ```shell
    curl -X 'GET' \
    'http://localhost:5555/api/v1/auth/test-token' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer {{ MY_ACCESS_JWT_TOKEN }}'
    ```

* `/api/v1/auth/refresh`

    **POST** - given a `REFRESH_JWT_TOKEN` returns a new `ACCESS_JWT_TOKEN`

    **body**

    ```json
    {
        "refresh_token": "{{ MY_JWT_REFRESH_TOKEN }}"
    }
    ```
    
    **curl**

    ```shell
    curl -X 'POST' \
    'http://localhost:5555/api/v1/auth/refresh' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "refresh_token": "{{ MY_JWT_REFRESH_TOKEN }}"
    }'
    ```



#### [Two Factor Authentication](#two-factor-authentication)

* `/api/v1/tfa/login_tfa?tfa_token=`

    **POST** - it's the second step after login for users with TFA enabled, it is necessary to have the TOTP token and to have the temporary access token in `Authorization` header returned by `login` endpoint for users with TFA enabled
    
    **curl**

    ```shell
    curl -X 'POST' \
    'http://localhost:5555/api/v1/tfa/login_tfa?tfa_token={{ MY_TOTP_TOKEN }}' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer {{ MY_PRE_TFA_JWT_ACCESS_TOKEN }}' \
    -d ''
    ```

* `/api/v1/tfa/recover_tfa?tfa_backup_token=`

    **POST** - it's the second step after login for users with TFA enabled that can't receive/recover their TOTP token, so they can use one of the backup tokens sent in signup step. It is necessary to have the temporary access token in `Authorization` header returned by `login` endpoint for users with TFA enabled
    
    **curl**

    ```shell
    curl -X 'POST' \
    'http://localhost:5555/api/v1/tfa/recover_tfa?tfa_backup_token={{ MY_BACKUP_TOTP_TOKEN }}' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer {{ MY_PRE_TFA_JWT_ACCESS_TOKEN }}' \
    -d ''
    ```

* `/api/v1/tfa/get_my_qrcode`

    **GET** - authenticated endpoint to receive again its own qr code (only for user with `code_generator` device)
    
    **curl**

    ```shell
    curl -X 'GET' \
    'http://localhost:5555/api/v1/tfa/get_my_qrcode' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer {{ MY_JWT_ACCESS_TOKEN }}'  --output my_recovered_qr_code.png
    ```

* `/api/v1/tfa/enable_tfa`

    **PUT** - enables TFA for authenticated users that didn't enable it on signup step. `device_type` is one between `email` or `code_generator`

    **body**

    ```json
    {
        "device_type": "code_generator"
    }
    ```
    
    **curl** (the `--output` option will save on your filesystem a valid qr-code image only if device type is `code_generator`)

    ```shell
    curl -X 'PUT' \
    'http://localhost:5555/api/v1/tfa/enable_tfa' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer {{ MY_JWT_ACCESS_TOKEN }}' \
    -H 'Content-Type: application/json' \
    -d '{
    "device_type": "code_generator"
    }' --output my_new_qr_code.png
    ```


#### [Users](#users)

* `/api/v1/users/users`

    **GET** - test non-authenticated endpoint to get all users in DB
    
    **curl**

    ```shell
    curl -X 'GET' \
    'http://localhost:5555/api/v1/users/users' \
    -H 'accept: application/json'
    ```

#### [Tasks](#tasks)

* `/api/v1/tasks/test-celery`

    **GET** - endpoint to test celery send mail function
    
    **curl**

    ```shell
    curl -X 'GET' \
    'http://localhost:5555/api/v1/tasks/test-celery' \
    -H 'accept: application/json'
    ```

* `/api/v1/tasks/taskstatus?task_id=`

    **GET** - endpoint to retrieve task status. `?task_id` is returned by ``/api/v1/tasks/test-celery` endpoint
    
    **curl**

    ```shell
    curl -X 'GET' \
    'http://localhost:5555/api/v1/tasks/taskstatus?task_id={{ TASK_ID }}' \
    -H 'accept: application/json'
    ```

### **[Crud](#crud)**
The modules inside this package are responsible to query the DB

### **[Core](#core)**
The modules inside this package are responsible to handle the core business logic of the application

__________
__________

## [Run from docker-compose](#run-from-docker-compose)

To run all the services, from the application root run:

```shell
docker-compose -f docker/docker-compose.yaml up  
```

The FastAPI server is exposed on port `5555`, FastAPI swagger is available at http://localhost:5555/docs#/

---

To follow only FastAPI logs, from another terminal, run:
```shell
docker logs --tail 200 -f fastapi_2fa  
```

---

To run tests, from another terminal, run:
```shell
docker exec fastapi_2fa pytest --cov-report term --cov=fastapi_2fa tests/       
```

__________
__________

## [Todos](#todos)

* reset / recover password
* encrypt backup tokens
* throttling for failed login
* complete tests
* logging