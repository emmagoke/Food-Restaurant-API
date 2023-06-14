# Food Restaurant API


## Food Restaurant API

This is an API that provide endpoints for Categories , Menuitem, Orders, Cart and Order. The API also handles authentication using token base 



## Local Requirement
- Requires Python 3.7 or Later
- Pipenv
- Django 3.2 or Later
- DjangoRestFrameWork
- Djoser

#### Virtual Environment

I recommend working `pipenv` whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment using `pipenv` for your platform can be found in the [pipenv docs](https://pipenv.pypa.io/en/latest/index.html)

##### To Create a virtual Environment



## Endpoints

###  User registration and token generation endpoints 
#### POST '/api/users'
- `Role` - No role required
- `Purpose` - Creates a new user with name, email and password
- Request(`payload`): name, email, password
#### GET '/api/users/me/'
- `Role` - Anyone with a valid user token
- Displays only the current user
- Request(`auth token`) - `prefix` - (Token), token_generated for the user.
#### POST '/api/token/login/'
- `Role` - Anyone with a valid username and password
- `Purpose` - Generates access tokens that can be used in other API calls in this Django project
- Request(`auth token`) - `prefix` - (Token), token_generated for the user.


### Menu-items endpoints
#### GET '/api/categories'
- `Role` - 
- `Purpose` - Gets a dictionary of categories from the Category database in which the keys are the ids and the value is the corresponding category in string format.
- Request: None
- Response: An object  that contains the id, title and slug of all the categories in the database.

>Example: `curl http://127.0.0.1:8000/api/categories`
