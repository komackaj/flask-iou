# Flask-IOU
Local exchange network platform based on trusted IOUs. Similar concept as [Villages](https://villages.io/), different implementation.

### How to run
Using dependencies from PyPi. Run from project root. Edit iou/config.py according to your needs (especially googleAuth section).
```bash
$ pip3 install -r requirements.txt
$ python3 -m unittest discover test
$ ./iou.py --create-tables
$ export OAUTHLIB_INSECURE_TRANSPORT=1
$ export OAUTHLIB_RELAX_TOKEN_SCOPE=1
$ ./iou.py --debug
```

Application is now available at http://localhost:5000/.
