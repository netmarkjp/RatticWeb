RatticWeb
=========

Build Status on netmarkjp/RatticWeb : [![Build Status](https://travis-ci.org/netmarkjp/RatticWeb.png?branch=master)](https://travis-ci.org/netmarkjp/RatticWeb)

RatticWeb is the website part of the Rattic password management solution, which allows you to easily manage your users and passwords.

If you decide to use RatticWeb you should take the following into account:
* The webpage should be served over HTTPS only, apart from a redirect from normal HTTP.
* The filesystem in which the database is stored should be protected with encryption.
* The access logs should be protected.
* The machine which serves RatticWeb should be protected from access.
* Tools like <a href=="http://www.ossec.net/">OSSEC</a> are your friend.

Support and Known Issues:
* Through <a href="http://twitter.com/RatticDB">twitter</a> or <a href="https://github.com/tildaslash/RatticWeb/issues?state=open">Github Issues</a>
* Apache config needs to have "WSGIPassAuthorization On" for the API keys to work  

Dev Setup: <https://github.com/tildaslash/RatticWeb/wiki/Development>

# Special setup topics on MacOSX

Segmentation fault will occure caused by zbar.

To avoid problem, use `npinchot/zbar` .

```
pip uninstall zbar
pip install git+https://github.com/npinchot/zbar.git
```
