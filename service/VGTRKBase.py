import time
from datetime import datetime
import re

import VGTRKBaseModel
from sqlalchemy import func


def verify_hour():

    time_now = time.time()
    result = VGTRKBaseModel.session.query(VGTRKBaseModel.Sys_LastUpdate).first()
    if result is None:
        return True
    elif time_now - result.datetime_lastUpdate.timestamp() > 3600.0:
        return True
    return False


def set_hour():

    time_now = time.time()

    result = VGTRKBaseModel.session.query(VGTRKBaseModel.Sys_LastUpdate).first()
    if result is None:
        result = VGTRKBaseModel.Sys_LastUpdate()
        #result.datetime_lastUpdate = datetime.fromtimestamp(time_now)
        VGTRKBaseModel.session.add(result)
    result.datetime_lastUpdate = datetime.fromtimestamp(time_now)
    VGTRKBaseModel.session.commit()


def get_or_insert_company(company_name):

    company = VGTRKBaseModel.session.query(VGTRKBaseModel.Company).\
        filter(VGTRKBaseModel.Company.company_name == company_name).first()

    if company is None:
        company = VGTRKBaseModel.Company(company_name)
        VGTRKBaseModel.session.add(company)
        VGTRKBaseModel.session.commit()

    return company.company_id


def get_or_insert_state(state_name):

    state = VGTRKBaseModel.session.query(VGTRKBaseModel.State).\
        filter(VGTRKBaseModel.State.state_name == state_name).first()
    if state is None:
        state = VGTRKBaseModel.State(state_name)
        VGTRKBaseModel.session.add(state)
        VGTRKBaseModel.session.commit()

    return state.state_id


def update_row(row):

    id_all = re.findall(r'.*\/(\d*)', row['href'])
    id = id_all[0]

    procurement = VGTRKBaseModel.session.query(VGTRKBaseModel.Procurement).\
        filter(VGTRKBaseModel.Procurement.procurement_id == id).first()

    if procurement is None:

        procurement = VGTRKBaseModel.Procurement()

        procurement.procurement_id = id
        procurement.procurement_num = row['num']
        procurement.procurement_description = row['description']
        procurement.procurement_href = row['href']
        procurement.procurement_price = row['price']

        if row['start'] != '':
            procurement.procurement_start = datetime.strptime(row['start'], '%d.%m.%Y %H:%M:%S')
        if row['finish'] != '':
            procurement.procurement_finish = datetime.strptime(row['finish'], '%d.%m.%Y %H:%M:%S')

        procurement.procurement_company_id = get_or_insert_company(row['customer'])
        procurement.procurement_state_id = get_or_insert_state(row['state'])

        VGTRKBaseModel.session.add(procurement)
        VGTRKBaseModel.session.commit()
        return True

    return False


def get_rows(num, description):

    query = VGTRKBaseModel.session.query(VGTRKBaseModel.Procurement, VGTRKBaseModel.Company, VGTRKBaseModel.State)
    query = query.outerjoin(VGTRKBaseModel.Company,
                       VGTRKBaseModel.Company.company_id == VGTRKBaseModel.Procurement.procurement_company_id)
    query = query.outerjoin(VGTRKBaseModel.State,
                       VGTRKBaseModel.State.state_id == VGTRKBaseModel.Procurement.procurement_state_id)

    if num != '':
        query = query.filter(VGTRKBaseModel.Procurement.procurement_num == num)
    if description != '':
        query = query.filter(VGTRKBaseModel.Procurement.procurement_description.ilike(f'%{description}%'))

    query.order_by(VGTRKBaseModel.Procurement.procurement_id.desc())
    records = query.all()
    rec = []
    for record in records:
        #print(record._asdict())
        d = {'href': record.Procurement.procurement_href, 'num': record.Procurement.procurement_num,
             'customer': record.Company.company_name, 'description': record.Procurement.procurement_description,
             'price': record.Procurement.procurement_price,
             'start': record.Procurement.procurement_start.strftime("%d.%m.%Y")
             if not record.Procurement.procurement_start is None else None,
             'finish': record.Procurement.procurement_finish.strftime("%d.%m.%Y")
             if not record.Procurement.procurement_finish is None else None,
             'state': record.State.state_name}
        rec.append(d)
    return rec
