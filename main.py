from flask import Flask, render_template, g
import psycopg2
import qsostats
import configparser
import argparse

app = Flask(__name__)

#arguments
parser = argparse.ArgumentParser()
parser.add_argument('--db-config-path', default='db_config.ini', help='Path to config file containing postgresql connection information.')
args = parser.parse_args()

#read config
db_config_path = args.db_config_path
db_config = configparser.ConfigParser()
db_config.read(db_config_path)
db_config = db_config['db_config']

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(dbname=db_config['dbname'],
                                         user=db_config['user'],
                                         password=db_config['password'],
                                         host=db_config['hostname'],
                                         port=db_config['port'])
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@app.route("/")
def index():
    db_connection = get_db()

    #counts
    count_today = qsostats.qso_count(db_connection, 1)[0]
    count_twomonths = qsostats.qso_count(db_connection, 2*31)[0]

    #rate
    rate = qsostats.current_qso_rate(db_connection)

    #collect in struct
    qsostats_dict = {'count_today': count_today,
                    'count_twomonths': count_twomonths,
                    'rate': rate}


    #get last QSOs
    last_qsos_list = qsostats.last_qsos(db_connection)

    return render_template('index.html', qsostats=qsostats_dict, last_qsos=last_qsos_list)

@app.errorhandler(Exception)
def errorhandler(error):
    return render_template('error.html', error_type=type(error))

if __name__ == "__main__":
    app.run()
