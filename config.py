from flaskext.mysql import MySQL
from app import app

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'valentine1004'
app.config['MYSQL_DATABASE_DB'] = 'simple_network'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)