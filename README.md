# Smart License - Demo Web-App

## About 

This is a python/django based application that demostrates:

- Creation of Smart Licenses with different Transaction Models
- Registration of Smart Licenses on the Content Blockchain
- Issuance and Transfer of Smart License Tokens

## Development Setup

This project requires Python 3 and a MultiChain node with RPC  access for 
local development and testing.

It is recommended to use a python virtualenv for development. Install 
dependencies in your activated virtualenv with pip install -r requirements.txt. 
Create your configuration in smartlicense/settings/config.py 
(see sample_config.py). Get your development environment up and running with 
these commands:

````bash
fab reset
python manage.py runserver
````

`fab reset` will:

- update requirements
- remove development db
- delete, re create and run migrations
- create a demo user (user: demo, password: demo)
- load fixtures and demo content
- import your multichain nodes wallet address

After starting your the app with python manage.py runserver visit the backend
at http://127.0.0.0:8000/demo/
