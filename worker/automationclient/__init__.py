import os

automationserver_url = os.getenv('ATS_URL') or "http://localhost:8000/api"
automationserver_token = os.getenv('ATS_TOKEN') or ""

headers = { "Authorization Bearer": automationserver_token } if automationserver_token else {}