# Recipes

It's created on [FastAPI](https://github.com/tiangolo/fastapi) web app with API, authentication (based on [FastAPI users](https://github.com/fastapi-users/fastapi-users)), etc.

<br>

![App's light theme screenshot](/screenshots/home-page-light-theme.jpg)

![App's dark theme screenshot](/screenshots/home-page-dark-theme.jpg)

## Run

To run this app, you need:

1. Clone this repository.

```powershell
git clone https://github.com/tiomchik/recipes-web-app.git
```

2. Create and activate virtual enviroment.

Windows:
```powershell
py -m venv .venv
& venv/scripts/activate.ps1
```
UNIX:
```bash
python3 -m venv .venv
source venv/scripts/activate
```

3. Install the requirements.

```powershell
pip install -r requirements.txt
```

4. Run migrations.

```powershell
alembic upgrade head
```

5. Change directory to src folder and run local server

```powershell
cd src
uvicorn main:app --reload
```

or if you want run on another port:

```powershell
uvicorn main:app --reload --port=PORT
```

6. Go to http://localhost:8000/ or to a port you specified.

## Tests

To run tests, write this in terminal (from project root directory):

```powershell
cd tests
pytest . -s -v
```

## License

Code is licensed under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
