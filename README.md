
# rasa commands
pip install mysql-connector-python - to install mysql.connector
python -m venv .\venv  - to create virtual environment
.\venv\scripts\activate - to activate venv that is created--do this in each terminal
rasa train- to train model
rasa shell - to run rasa on terminal
rasa run - to run rasa on postman 
rasa run actions - to run rasa action.py file
rasa interaction - proper conversation with bot  yes/no 
rasa run --enable-api --cors "*"

# to test rasa server
1.http://localhost:5005/status
2.http://localhost:5005
3.http://localhost:5005/version
4.http://localhost:5005/conversations/<conversation_id>/tracker  (use tracker as conversation_id)

# to test rasa action server 
3.http://localhost:5055/health

# how to run rasa and swagger ui
4 terminals :
In all 4 terminals start virtual environment- .\venv\scripts\activate
1. in root project, rasa run --enable-api --cors "*" : 5005
2. in root project, rasa run actions                 : 5055
3. in root project, python cors_server.py            : 3200
4. in swagger-ui, python -m http.server 8000         : 8000

http://localhost:3200/ in browser
http://localhost:8000/swagger.yaml in explore

Why do you open http://localhost:3200 in browser instead of 8000?
Because:
The swagger-ui (static HTML/JS files) is served on port 8000.
But those files make API requests to your Rasa server (:5005).
Browsers block cross-origin requests (CORS) unless configured.
That’s why you’re running cors_server.py → it acts as a proxy and makes Rasa available at http://localhost:3200 with CORS enabled.

So:
You open Swagger at http://localhost:3200 (served through your proxy).
Inside Swagger’s “Explore” field, you load your spec file → e.g. http://localhost:8000/swagger.yaml.

# to run multiple sessions ie multiple users 
"rasa shell --port 5006" - change port no cuz bydefault it is 5005 port no
to change duration of session it is there in domain.yml in session_config in minutes and keep false to avoid taking same slots for next session
