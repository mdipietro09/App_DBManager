
import os

#ENV = "DEV"
ENV = "PROD"


## server
host = "0.0.0.0"
port = int(os.environ.get("PORT", 5000))


## info
app_name = "DBManager"
contacts = "https://www.linkedin.com/in/mauro-di-pietro-56a1366b/"
code = "https://github.com/mdipietro09/App_DBManager"
tutorial = ""
fontawesome = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"

about = ""

## fs
#root = os.path.dirname(os.path.dirname(__file__)) + "/"