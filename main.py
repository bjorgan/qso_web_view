from flask import Flask, render_template
import psycopg2
import qsostats
import configparser

app = Flask(__name__)

#read config
db_config_path = 'db_config.ini'
db_config = configparser.ConfigParser()
db_config.read(db_config_path)
db_config = db_config['db_config']

#database connection
db_connection = psycopg2.connect(dbname=db_config['dbname'],
                                 user=db_config['user'],
                                 password=db_config['password'],
                                 host=db_config['hostname'],
                                 port=db_config['port'])

@app.route("/")
def index():
    #counts
    count_today = qsostats.qso_count(db_connection, 1)[0]
    count_twomonths = qsostats.qso_count(db_connection, 2*31)[0]

    #rate
    rate = qsostats.current_qso_rate(db_connection)
    print(rate)

    #collect in struct
    qsostats_dict = {'count_today': count_today,
                'count_twomonths': count_twomonths,
                'rate': rate}


    #get last QSOs
    last_qsos_list = qsostats.last_qsos(db_connection)

    return render_template('index.html', qsostats=qsostats_dict, last_qsos=last_qsos_list)

if __name__ == "__main__":
    app.run()
