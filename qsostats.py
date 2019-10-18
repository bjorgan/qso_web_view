"""
Calculate various QSO statistics from QSO database.
"""

from datetime import datetime, timedelta

def last_qsos(qso_db_connection, number=10):
    c = qso_db_connection.cursor()
    c.execute('SELECT timestamp, operator, call FROM qsos ORDER BY timestamp DESC LIMIT %s', (number,))
    last_qsos = c.fetchall()
    return last_qsos

def current_qso_rate(qso_db_connection):
    """
    Calculate current QSO rate as number of QSOs within the last hour over the
    time difference between first and last QSO.
    """
    import numpy as np
    c = qso_db_connection.cursor()

    #fetch timestamps of QSOs within one hour
    c.execute('SELECT timestamp from qsos WHERE timestamp > %s', (n_days_ago(1.0/24.0),))
    data = c.fetchall()
    if len(data) > 0:
      timestamp = np.array(data)[:, 0].astype(str).astype(np.datetime64)
      timerange = (timestamp - timestamp[0]).astype(int)[-1]/60.0/60.0
      num_qsos = len(timestamp)
      return int(round(num_qsos/timerange))
    else:
      return 0

def qso_count(qso_db_connection, days):
    """
    Get the number of QSOs from a given number of days ago until now.

    Parameters
    ----------
    days: float
        Number of days. Specify day fractions in order to get hour/minute
        resolution.

    Returns
    -------
    all_qsos: int
        Number of QSOs
    dx_qsos: int
        Number of DX QSOs (assuming non-european)
    """
    c = qso_db_connection.cursor()

    #fetch all QSOs
    c.execute('''SELECT count(*) FROM qsos WHERE timestamp > %s''', (n_days_ago(days),))
    all_qsos = c.fetchone()[0]

    #fetch DX qsos
    c.execute('''SELECT count(*) FROM qsos WHERE timestamp > %s AND continent != 'EU' ''', (n_days_ago(days),))
    dx_qsos = c.fetchone()[0]
    return all_qsos, dx_qsos

def n_days_ago(days):
    """
    Get a date time string for the date n days ago.

    Parameters
    ----------
    days: float
        Number of days ago. Accepts day fractions.
    Returns
    -------
    date_str: str
        String on format YYYY-MM-DD HH:MM a specific number of days ago.
    """
    date_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
    return date_str

