<p align='center'>
<h1>Interact With Text (IWT)</h1><
<h5>Interactive text, allows its users to interact with texts to produce text-to-speech reading and translation, via clicking and hovering</h5>
( <a href='http://iwt.serveo.net/'>Live server</a> )
<br /> <br />
<img src="https://audio-sequence.github.io/iwt.gif">
<br />
</p>

#### Setup:
- `pip3 install -r requirements.txt`

> Side step, you must add `IWT/secrets.py` file that contains your own keys:
```python
secrets = {
    'RECAPTCHA_PRIVATE_KEY': '',
    'RECAPTCHA_PUBLIC_KEY': '',
    'SECRET_KEY': ''}
```
- `python3.6 manage.py makemigrations`
- `python3.6 manage.py migrate`
- `python3.6 manage.py runserver`