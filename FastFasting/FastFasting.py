from datetime import datetime
import os
import sqlite3
import ui

db_connection = ''
cursor = ''


@ui.in_background
def ToggleFasting(sender):
    ''' The start/stop button was pressed '''
    print("Sender: %s", sender)
    global db_connection
    global cursor
    started = get_status(cursor)
    if started:
       sender.title = 'Start period'
    else:
       sender.title = 'Stop period'
    add_time_to_db(db_connection, cursor, started)


@ui.in_background
def RefreshPressed(sender):
    ''' The refresh button was pressed '''
    global cursor
    StartStop = sender.superview['StartStop']
    started = get_status(cursor)
    if started:
       StartStop.title = 'Stop period'
    else:
       StartStop.title = 'Start period'
    pass


def connect_db(fname):
    ''' connect to sqlite3 db or create if missing '''
    global db_connection
    global cursor
    create_tables = False
    if not os.path.isfile(fname):  # no such file
        create_tables = True
    db_connection = sqlite3.connect(fname)  #, check_same_thread=False)
    cursor = db_connection.cursor()
    if create_tables:
        cursor.execute('''CREATE TABLE fasting
                        (Id integer primary key autoincrement,
                        start_time text,
                        stop_time text)''')


def list_database(cursor):
    ''' list all database intries '''
    sql = 'SELECT * FROM fasting WHERE Id = (SELECT MAX(Id) FROM fasting)'
    cursor.execute(sql)
    return cursor.fetchall()


def last_db_entry(cursor):
    ''' return rowid + data from last db insert '''
    # sql = 'SELECT rowid,* FROM fasting ORDER BY start_time DESC LIMIT 1'
    sql = 'SELECT * FROM fasting WHERE Id = (SELECT MAX(Id) FROM fasting)'
    cursor.execute(sql)
    return cursor.fetchall()


def get_status(cursor):
    ''' determine if a period is "open" '''
    last_entry = last_db_entry(cursor)
    if not last_entry:   # db empty
        return False
    id, start_time, stop_time = last_entry[0]
    if start_time and stop_time:  # last was started and stopped
        return False
    return True


def add_time_to_db(db_connection, cursor, started):
    ''' Add current time on format "2022-11-05 21:51" to database '''
    now_time = datetime.now()
    time_string = now_time.strftime('%Y-%m-%d %H:%M')
    if not started:
        cursor.execute('''INSERT INTO fasting(start_time, stop_time)
                       VALUES(?,?)''', (time_string, ''))
        db_connection.commit()
    else:
        rowid, started, stopped = last_db_entry(cursor)[0]
        cursor.execute('''UPDATE fasting SET stop_time=? where rowid=?''',
                       (time_string, rowid))
        db_connection.commit()


def main():
    ''' database initialization before loading gui ''' 
    fname = 'FastFasting.db'
    connect_db(fname)
    # The load must appear after defining the ui actions
    v = ui.load_view('FastFasting')
    v.present('sheet')



if __name__ == "__main__":
    main()
