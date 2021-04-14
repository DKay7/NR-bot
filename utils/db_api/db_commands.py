from datetime import datetime
from utils.db_api.db import db


def is_registered_master(uid):
    if db.masters.count_documents({'uid': uid, 'status': 1}) > 0:
        return True
    return False


def add_master(uid, data):
    id = db.masters.count_documents({}) + 1
    data['id'] = id
    data['status'] = 0
    data['start_date'] = '-'
    db.masters.insert_one(data)


def get_masters():
    masters = []
    for i in db.masters.find({'status': 1}):
        masters.append(i)
    return masters


def current_status():
    if db.settings.count_documents({'name': 'settings'}) > 0:
        r = db.settings.find_one({'name': 'settings'})
        return r['status']
    else:
        db.settings.insert_one({'name': 'settings', 'status': False})
        return False


def set_status(status):
    db.settings.update_one({'name': 'settings'}, {'$set': {'status': status}}, upsert=True)


def approve_master(uid):
    db.masters.update_one({'uid': uid, 'status': 0},
                          {'$set':
                               {
                                'status': 1,
                                'start_date': datetime.now().strftime("%d.%m.%Y %X"),
                                }
                           })


def add_ticket(data):
    id = db.tickets.count_documents({}) + 1
    data['id'] = id
    db.tickets.insert_one(data)

    return id


def update_ticket_if_available(uid, master_id):
    if db.tickets.count_documents({'id': uid, 'status': 0}) > 0:
        db.tickets.update_one({'id': uid}, {'$set':
                                                {'master': get_master_name_by_id(master_id),
                                                 'accept_date': datetime.now().strftime("%d.%m.%Y %X"),
                                                 'status': 1,}}, upsert=True)

        return db.tickets.find_one({'id': uid})
    return False


def decline(uid, master_name):
    if db.tickets.count_documents({'id': uid}) > 0:
        den_index = db.tickets.find_one({'id': uid})['den_index']
        db.tickets.update_one({'id': uid}, {'$set': {'master': '-', 'accept_date': '-',
                                                     'status': 0, f'denied_{den_index % 3}': master_name
                                                     }}, upsert=True)
        db.tickets.update_one({'id': uid}, {'$inc': {'den_index': 1}})
        return db.tickets.find_one({'id': uid})
    return False


def confirm(uid, data):
    if db.tickets.count_documents({'id': uid}) > 0:
        db.tickets.update_one({'id': uid},
                              {'$set': {'status': 2,
                                        'confirm_date': datetime.now().strftime("%d.%m.%Y %X"),
                                        'final_price': data['final_price'],
                                        'final_work': data['final_work'],
                                        'is_client_happy': data['is_client_happy'],
                                        }},
                              upsert=True)

        return db.tickets.find_one({'id': uid})
    return False


def get_master_name_by_id(uid):
    f = db.masters.find_one({'uid': uid})
    return f["name"]


def get_master_by_name(name):
    f = db.masters.find_one({"name": name})
    return f


def get_tickets(id=None):
    if id is None:
        data = []
        for i in db.tickets.find({}):
            data.append(i)
    else:
        data=[]
        for i in db.tickets.find({'master': get_master_name_by_id(id), 'status': 1}):
            data.append(i)
    return data


def get_actual_tickets():
    data = []
    for i in db.tickets.find({'status': 0}):
        data.append(i)
    return data


def delete_master(uid):
    db.masters.delete_one({'uid': uid})


def archive(uid):
    if db.tickets.count_documents({'id': uid}) > 0:
        db.tickets.update_one({'id': uid}, {'$set': {'status': 5}}, upsert=True)
        return True
    return False


def get_ticket_by_id(tid):
    return db.tickets.find_one({'id': tid})


def get_master_by_uid(uid):
    return db.masters.find_one({'uid': uid})


def update_ticket(tid, status):
    db.tickets.update_one({'id': tid},
                          {'$set': {'status': 0,
                                    'confirm_date': '-',
                                    'master': '-',
                                    'accept_date': '-',
                                    'final_price': '-'}})
