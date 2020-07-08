# The Opening hours project.
==========================

Simple app to help customers, check out opening hours .

1 Installation
---------------
First you need to clone this repository.
>git clone https://github.com/AndryTverdyj/isopen.git

2 Usage
--------

Move on to directory isopen
Install requirements into virtualenv (see: virtualenv setup)

>pip install -r requirements.txt

The project requires Python3.6.* or newest

3 Running
-----------------------
Start this project running next command:

>uvicorn main:app

Check it out http://127.0.0.1:8000/docs

4 Backend API
-----------------

There are two endpoints
1) /stations/{1d}/isopen/
id - (Stations id : integer )
return boolean value

2) /stations/{id}/next/
return text message about next event (For example: if station is open right now it will return message when this station will be closed )
