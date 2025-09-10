# Project 4: 'TellMe Messaging Application' 

![Image of the site interface](/public/images/TellMe.PNG)

### Introduction

While thinking of an Idea for this project I wanted to try something new, something that I could learn from and explore. I had previously wanted to work with making an application where I could send messages to my friends and the other way around, I thought it would be a cool concept and that's where the inspiration for TellMe came from. Similar to already existing platforms for messaging I took inspiration to build my own version and to see how close I can get in one week.
### Technologies Used

- CSS3
- JavaScript
- PostgresSQL
- Django
- Python
- Channel/Channel Redis
- Websockets
- Uvicorn
- Redis
- GitHub

### Get Started

- Instructions: As of yet the application is not deployed, below I will go through a set of instructions as to how you can get the application on your local desktop and proceed with seting things up until the part where you can start using the application freely.

## Clone Repository

To start lets first clone the repo, you can choose to have it in any directory or destination on your personal device:

```
git clone https://github.com/Ab-875/TellMe-chatting-application.git
```

## Setup and Install Python/Django

First we will need to download any version of python 3.4 and later, you can find and download python at the link below and follow any installation guide online:

- [Download Python](https://www.python.org/downloads/)

Usually pip comes with downloading python but to make sure it is there run the following command into your terminal:

```
pip --version
```
Once you confirm that pip has a latest version you are good to go, if not then troubleshoot your installation or run the following command into your terminal to install pip:

```
python -m pip install --upgrade pip
```

## Setup your Virtual Environment

In the project directory lets setup a virtual environment:

```
python -m venv name-of-venv
```

name-of-venv can be anything to your choosing

and then run the environment:

Windows:
```
source name-of-venv/scripts/activate
```
Mac:
```
source name-of-venv/bin/activate
```

## Install Django and packages

Now lets install all our packages that are related to this project after confirming we are in the venv, we can check by doing ```which python``` and confirming we are in the venv:

```
pip install
```
## Setup your PostgresSQL database

Follow a guide online to setup your postgresSQL database, after setup create a database and name it to your liking, after doing that head over to settings.py in the project folder and look for the following:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'name-of-database', 
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',  
        'PORT': '5432',
    }
}

```

it would look slightly differant than mine but all you have to do is change the name to the name of your database and the password to the password you used to setup your postgres account

## Download and Setup Memurai

Memurai will act as our server for this project, download and follow the instructions in the link below, however if you're not confidant with setting this up follow the next step instead to setup server locally:

- [Memurai Download Link](https://www.python.org/downloads/)
If you want to set it up locally navigate to the settings.py in the project until you find this:

```
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

Once you find it change it to this:

```
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

## Run The Code
After the setup all you have to do is run this command into the terminal
```
uvicorn messaging_app.asgi:application --port 8000 --reload
```

Now in your browser head over to port 8000 on your localhost and the application should be up and running.


### Development

I will keep the rundown of development for this project short and to the point without giving too much details but you're always free to ask me about parts of the code or inspect the code itself. As stated in previous steps the main building framework for this project is Django, in other words Python. I was somewhat familiar to websocket application in python prior to starting this porject hence why I chose to go with Django. Initially I wanted to run my Redis channel layer through docker to setup chatroom connections but due to hardware limitations I looked for an alternative and went with MeMurai, a third-party Redis partner that natively ports Redis for windows.

Working with channel connections and websockets was confusing at first, and I still do face some challanges in understanding some parts of the code so the features were limited in the end but for my application as long as the connection was established that's all I needed for the chatroom.

As you might know Django does not offer dynamic page rendering such as React so I needed a way to refresh my pages whenever a message was sent through the connection, I did setup some scripts on my chatroom pages to deal with such problems so that everything happening in the chatroom is in real time.

### Next Step

- Add a friends list
- Considering moving the project to a REST framework
- Work on a notification system
- Clean up some of the CSS
- Deploy the application
- Different message formats such as voice or map locations and so on

### Conclusion

I think for me this project was both my last GA project to round up all I learned and also it was kind of my first project exploring ideas by myself and seeing what I can do with them, we were'nt instructed to build something as similar as this so 70% of the project was through my own research and reading documentation. I am happy with how it turned out in 1 week but I could have added more and there are room for improvement