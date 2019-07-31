# News reader

The project is built with:

- [Python](https://www.python.org/)
- [Flask](http://flask.pocoo.org/)

### Installing dependencies

- Install [pip](https://pip.pypa.io/en/stable/installing/), for Ubuntu that is: `sudo apt-get update` and `sudo apt-get install python-pip`
- Install the Python dependencies: 
  - `sudo pip install Flask`
  - `sudo pip install feedparser`

### Developing

- Run `python reader.py` and open localhost:5000 in a browser 

### Deploying to Apache on a Virtual Private Server

- Install the dependencies on the VPS
- Install the Apache web server: `sudo apt-get install apache2`
- Install WSGI: `sudo apt-get install libapache2-mod-wsgi`
- Copy the code to /var/www/flask-news-reader on the VPS
- Configure Apache by moving the reader.conf file from the project root to /etc/apache2/sites-available, and then disable the default site, enable the new site and restart the web server by running:
  - `sudo a2dissite 000-default.conf`
  - `sudo a2ensite reader.conf`
  - `sudo service apache2 reload`
- Check for errors: `sudo tail -f /var/log/apache2/error.log`

### Note

Use [Python virtual environments](http://modwsgi.readthedocs.io/en/develop/user-guides/virtual-environments.html) for production
