RatticWeb
=========

Build Status on netmarkjp/RatticWeb : [![Build Status](https://travis-ci.org/netmarkjp/RatticWeb.png?branch=master)](https://travis-ci.org/netmarkjp/RatticWeb)

----

RatticWeb is the website part of the Rattic password management solution, which allows you to easily manage your users and passwords.

If you decide to use RatticWeb you should take the following into account:
* The webpage should be served over HTTPS only, apart from a redirect from normal HTTP.
* The filesystem in which the database is stored should be protected with encryption.
* The access logs should be protected.
* The machine which serves RatticWeb should be protected from access.
* Tools like <a href="http://www.ossec.net/">OSSEC</a> are your friend.

Support and Known Issues:
* Through <a href="http://twitter.com/RatticDB">twitter</a> or <a href="https://github.com/tildaslash/RatticWeb/issues?state=open">Github Issues</a>
* Apache config needs to have "WSGIPassAuthorization On" for the API keys to work  

Dev Setup: <https://github.com/tildaslash/RatticWeb/wiki/Development>

----

# Difference from original RatticWeb

- Drop Python 2.6 support => Only Python 2.7
- Update django to 1.8 and also update some modules.
- UserProfile: New fature RatticWeb can use as Two Factor Auth Device
    - Read QR Image, and show 6 numbers
- Credential: New fature RatticWeb can use as Two Factor Auth Device
    - Read QR Image, and show 6 numbers
- Credential: Change Cred.title max length 64 => 255

Note: When you use MySQL, `python manage.py migrate auth` must run before `python manage.py migrate`

# Supported QR Image format

It depends on PIL(Pillow).

If you support JPEG, you may have to install libjpeg-devel before `pip install` .

CentOS7 example:

```
sudo yum install libjpeg-turbo-devel
```

# How to use with MySQL

Do `migrate auth` before `migrate` .

```bash
$ mysql -u root -h 127.0.0.1 -P 3306 -e 'create database rattic character set utf8 collate utf8_unicode_ci;'
$ python manage.py makemigrations
$ python manage.py migrate auth
$ python manage.py migrate
$ python manage.py createsuperuser --username rattic --email rattic@example.com
```

# Special setup topics on MacOSX

Segmentation fault will occure caused by zbar.

To avoid problem, use `npinchot/zbar` .

```
pip uninstall zbar
pip install git+https://github.com/npinchot/zbar.git
```
