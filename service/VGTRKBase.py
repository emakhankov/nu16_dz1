import sqlite3
import time
import re


def get_conn():

    conn = sqlite3.connect('service/database.sqllite3.db')
    return conn


def verify_hour():

    time_now = time.time()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('select datetime_lastUpdate from Sys_LastUpdate where key=:key', {'key': 'hour'})
    result = cur.fetchone()

    conn.close()
    if result is None:
        return True
    elif time_now - result[0] > 3600.0:
        return True
    return False


def set_hour():

    time_now = time.time()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute('delete from Sys_LastUpdate where key=:key', {'key': 'hour'})
    cur.execute('insert into Sys_LastUpdate (key, datetime_lastUpdate) values (:key, :time)',
                {'key': 'hour', 'time': time_now})
    conn.commit()
    conn.close()

def get_or_insert_company(company_name):

    conn = get_conn()
    cur = conn.cursor()
    dic = {'company_name': company_name}
    cur.execute('Select company_id from Companies where company_name = :company_name', dic)
    result = cur.fetchone()
    if result is None:

        cur.execute('insert into Companies (company_name) values (:company_name)', dic)
        conn.commit()
        cur.execute('Select company_id from Companies where company_name = :company_name', dic)
        result = cur.fetchone()

    return result[0]


def get_or_insert_state(state_name):
    conn = get_conn()
    cur = conn.cursor()
    dic = {'state_name': state_name}
    cur.execute('Select state_id from States where state_name = :state_name', dic)
    result = cur.fetchone()
    if result is None:
        cur.execute('insert into States (state_name) values (:state_name)', dic)
        conn.commit()
        cur.execute('Select state_id from States where state_name = :state_name', dic)
        result = cur.fetchone()

    return result[0]


def update_row(row):
    conn = get_conn()
    cur = conn.cursor()

    id_all = re.findall(r'.*\/(\d*)', row['href'])
    id = id_all[0]

    row_db = {'procurement_id': id,
              'procurement_num': row['num'], 'procurement_description': row['description'],
              'procurement_href': row['href'], 'procurement_price': row['price'],
              'procurement_start': row['start'], 'procurement_finish': row['finish'],
              'procurement_company_id': get_or_insert_company(row['customer']),
              'procurement_state_id':  get_or_insert_state(row['state'])}

    cur.execute("select procurement_num from Procurements where procurement_id = :procurement_id", row_db)
    result = cur.fetchone()
    if result is None:
        sql = 'insert into Procurements (procurement_id, procurement_num, procurement_href, procurement_company_id,' \
                    ' procurement_description, procurement_price, procurement_start, procurement_finish,' \
                    ' procurement_state_id)  ' \
                    ' values (:procurement_id, :procurement_num, :procurement_href, :procurement_company_id, ' \
                    ' :procurement_description, :procurement_price, :procurement_start, :procurement_finish,' \
                    ' :procurement_state_id )'
        cur.execute(sql, row_db)
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False


def get_rows(num, description):

    sql = 'select p.procurement_num as num, ' \
          'p.procurement_href as href, ' \
          'c.company_name as customer, ' \
          'p.procurement_description as description, ' \
          'p.procurement_price as price, ' \
          'p.procurement_start as start, ' \
          'p.procurement_finish as finish, ' \
          's.state_name as state ' \
          'from Procurements p left join Companies c on p.procurement_company_id = c.company_id ' \
          'left join States s on p.procurement_state_id = s.state_id '

    sql_where = ''

    if num != '':
        sql_where = ' and p.procurement_num = :procurement_num '
    if description != '':
        sql_where = sql_where + ' and p.procurement_description like :procurement_description'

    if sql_where:
        sql_where = ' where ' + sql_where[4:]

    sql = sql + sql_where + ' order by p.procurement_id desc'

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, {'procurement_num': num, 'procurement_description': f'%{description}%'})

    columns = cur.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cur.fetchall()]

    return result
