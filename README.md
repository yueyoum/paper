# Paper

This is a simple blog based on bottle.


## Demo

* my blog: [Yueyoum](http://codeshift.org)




## Quick Start

details see **Deploy**

    git clone https://github.com/yueyoum/paper.git
    cd paper

    cp settings.py.example settings.py
    vim settings.py
    echo "this is me" > templates/me.html

    make init
    make database
    make key
    make run

Then you can visit the demo at http://127.0.0.1:8999
(static file will **not** be served)

For static files, you need nignx, or set DEBUG = True in settings.py


## Deploy

1.  using git or download **paper** directly.
2.  settings

        cp settings.py.example settings.py

    your should modify the settings with your needs

3.  set up a html page for /about link

    create a **me.html** file in templates folder.
    this page will show in /about link

4.  paper use virtualenv to running in a independent python environments.
    run this commands below:

        make init

6.  paper use sqlalchemy as ORM, so sync table metadata to DB

        make database


5.  generate the key for post blog.

    you will using [paper-client](https://github.com/yueyoum/paper-client) to post blog. so, this key is used for security.

        make key

6.  start the web

    gunicorn with gevent_pywsgi workers will serve the web at 127.0.0.1:8999

        make run

7.  config nginx
    
    there is a nginx config file located at deploy folder,
    copy and modify it to make nginx serve **paper**


## How to post blog

**paper** is designed for writing markdown at local,
you need [paper-client](https://github.com/yueyoum/paper-client) 
to post markdown.

At the step 5 above, we make the security key via **make key**.
the key file is located at src/ folder.

**cat src/\_key**, and you will get the security key, copy it.
It will be used for paper_client.conf.

details see [paper-client](https://github.com/yueyoum/paper-client)

