# Paper

This is a simple blog based on bottle.

It's not a static blog generator. 


## Demo

* my blog: 


## Quick Start

details see **Deploy**

    ```bash
    git clone https://github.com/yueyoum/paper.git
    cd paper

    cp settings.py.example settings.py
    vim settings.py
    echo "this is me" > templates/me.html

    make init
    make database
    make key
    make run
    ```


## Deploy

1.  using git or download **paper** directly.
2.  settings

        ```bash
        cp settings.py.example settings.py
        ```

    your should modify the settings with your needs

3.  set up a html page for /about link
    create a **me.html** file in templates folder.
    this page will show in /about link

4.  paper use virtualenv to running in a independent python environments.
    run this commands below:

        ```bash
        make init
        ```

6.  paper use sqlalchemy as ORM, so sync table metadata to DB

        ```bash
        make database
        ```


5.  generate the key for post blog.
    you will using [paper-client]() to post blog. so, this key is used for security.

        ```bash
        make key
        ```

6.  start the web
    gunicorn with gevent_pywsgi workers will serve the web at 127.0.0.1:8999

        ```bash
        make run
        ```
