# Chatroom with socket

In this project I create a small room chat application using Flask-socketIO

## How to run

First create a venv folder:
```console
$ python3 -m venv venv
```

Then activate the venv:
```console
$ source venv/bin/activate
```

Install the dependencies:
```console
$ pip install -r requirements.txt
```

Run the server:
```console
$ python main.py
```

The server should then be running. Got to [http://localhost:5000](http://localhost:5000) with you browser and you will see and should be able to create new rooms or join some existing one with their code and witte some messages.

At the end, don't forget to stop the server by pressing `CRTL+C` and deactivate the venv when you're done:
```console
$ deactive
```