## Platform for educational courses

### Superuser 
Administrate all users and data, can create administrators and curators
### Administrator 
Can create courses, curators, administrate them, and see his learners
When permission access=False, Administrator has limitation:
* Can create only one course
* Can't create curator
* See only 5 learners
### Curator 
Can have a few administrators. 
See only courses and members of administrators with access. In other case doesn't see any courses and users of this administrator.
Has permission to review his courses, learners with access to these courses without contact information, and check home tasks
### Learner 
Can sign up, subscribe for courses, has permission to review his courses and do home tasks to them
When a learner subscribes to a course, they get access = False as default. He sees only lessons with free access status = True.
Administrator-owner of this course or superuser can change the learner permission to True.


Permission for Curator and Learner:
* If date_end is Null, permission unlimited
* Giving accesses to different courses by course id

### Lessons
Has free access status. If it's True, then learners can see it without permission. 

## Tech details

|**Resource**|**Resource Name**|**Version**|**Comment**|
| :-: | :-: | :-: | :-: |
|Back-end programming language|Python|3.10.5||
|Back-end web framework|Django|4.1.3||
|REST APIs toolkit|Django Rest Framework|3.14.0||
|Database|PostgreSQL|2.9.3||
|Web server||||

## Installation & Lunch

How to run a project locally?

1. Preparing

```sh
pip install pipenv
pipenv shell
pipenv install
```

2. Start server

```sh
python manage.py runserver
```

3. Stop server

```sh
Ctrl+C
```

4. Run migrations or database schema 
```sh
./manage.py migrate
```
5. Run unit tests 

```sh
./manage.py test
```

## Managing environment variables

Add some exports to your shell profile `~/.zshrc` or `~/.bashrc`<br>
Or paste these variables into `.env` file inside the project (without **export**)

```sh
export ENVIRONMENT = local    # environments keys (prod, local)

export SECRET_KEY=some_key

export DB_NAME = your_db_name ('courses_platform')
export DB_USER_NAME = your_user_name
export DB_PASSWORD = your_password
export DB_HOST = your_db_host
export DB_PORT = your_port_to_db (5432)
export ALLOWED_HOSTS = your_allowed_hosts []
export STATIC_URL = 'static/'

export DSN_KEY = your_key
export EMAIL_HOST_USER = your_host_user
export EMAIL_HOST_PASSWORD = your_email_for_host_user

export FRONT_END_DOMAIN_URL = your_domain_url
export FRONT_END_NEW_PASSWORD_PART = '/create_new_password'

export AWS_ACCESS_KEY_ID = your_aws_access_key
export AWS_SECRET_ACCESS_KEY = your_aws_secret_access_key
export AWS_STORAGE_BUCKET_NAME = your_aws_storage_bucket_name
```

Restart your terminal for changes to take effect.
