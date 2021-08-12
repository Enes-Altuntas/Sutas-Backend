from flask_jwt_extended import (
    jwt_refresh_token_required,
    get_jwt_identity)
from utils.exception import GenericException
import src.resources.endpoint.anounce as anounce
import json
import requests
from flask import jsonify
from config import config
from utils.token import Token

host = config['host']
client = config['client']


@jwt_refresh_token_required
@Token.check_refresh
def sendPass(request, app_db, ume_db):
    username = get_jwt_identity()
    user_info = ume_db.get_user_info(username)
    data = request.data
    parsed = json.loads(data)
    if user_info[0]['password'] == parsed['PASS']:
        ret = {
            'dialog': False,
        }
    return jsonify(ret), 200


@jwt_refresh_token_required
@Token.check_refresh
def getUsers(request, app_db, ume_db):
    try:
        users = ume_db.get_users()
    except:
        raise GenericException(
            "Kullanıcı bilgileri güncellenirken bir hata ile karşılaşıldı !", 403)

    ret = {
        'users': users,
    }
    return jsonify(ret), 200


@jwt_refresh_token_required
@Token.check_refresh
def update(request, app_db, ume_db):
    data = request.data
    parsed = json.loads(data)
    sapMsg = []

    try:
        if parsed['DATA']['user_type'] == 'SUP':
            parsed['DATA']['type_desc'] = 'Tedarikçi'
        elif parsed['DATA']['user_type'] == 'QTY':
            parsed['DATA']['type_desc'] = 'Kaliteci'
        elif parsed['DATA']['user_type'] == 'PUR':
            parsed['DATA']['type_desc'] = 'Satınalmacı'
        elif parsed['DATA']['user_type'] == 'PLA':
            parsed['DATA']['type_desc'] = 'Planlamacı'

        ume_db.modify_user(parsed['DATA'])
        u_type = parsed['DATA']['user_type'] + "_1"
        ume_db.modify_user_role(parsed['DATA']['username'], u_type)
        if parsed['DATA']['user_type'] == 'SUP':
            r = requests.get(host + 'add_user' + client,
                             params={'sup_id': parsed['DATA']['user_sys_id']}, verify=False)
            parsedSapData = json.loads(r.content)
            sapMsg = parsedSapData['OUT']

    except:
        raise GenericException(
            "Kullanıcı bilgileri güncellenirken bir hata ile karşılaşıldı !", 403)

    users = ume_db.get_users()

    ret = {
        'users': users,
        'sapMsg': sapMsg,
    }
    return jsonify(ret), 200


@jwt_refresh_token_required
@Token.check_refresh
def delete(request, app_db, ume_db):
    data = request.data
    parsed = json.loads(data)
    sapMsg = []

    try:
        ume_db.delete_user(parsed['DATA'])
        ume_db.delete_user_role(parsed['DATA'])
        if parsed['DATA']['user_type'] == 'SUP':
            r = requests.get(host + 'del_user' + client,
                             params={'sup_id': parsed['DATA']['user_sys_id']}, verify=False)
            parsedSapData = json.loads(r.content)
            sapMsg = parsedSapData['OUT']

    except:
        raise GenericException(
            "Kullanıcı silinirken bir hata ile karşılaşıldı !", 403)

    users = ume_db.get_users()

    ret = {
        'users': users,
        'sapMsg': sapMsg,
    }
    return jsonify(ret), 200
