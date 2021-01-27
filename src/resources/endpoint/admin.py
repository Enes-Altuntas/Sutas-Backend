from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity)
from utils.exception import GenericException
import src.resources.endpoint.anounce as anounce
import json
import requests
from flask import jsonify
from datetime import datetime, timedelta
from config import config

host = config['host']
client = config['client']


@jwt_refresh_token_required
def sendPass(request, ume_db, app_db):
    username = get_jwt_identity()
    user_info = ume_db.get_user_info(username)
    data = request.data
    parsed = json.loads(data)
    if user_info[0]['password'] == parsed['PASS']:
        ret = {
            'dialog': False,
            'refresh_token': create_refresh_token(identity=username)
        }
    return jsonify(ret), 200


@jwt_refresh_token_required
def getUsers(request, ume_db, app_db):
    username = get_jwt_identity()
    try:
        users = ume_db.get_users()
    except:
        raise GenericException(
            "Kullanıcı bilgileri güncellenirken bir hata ile karşılaşıldı !", 403)

    ret = {
        'users': users,
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200


@jwt_refresh_token_required
def update(request, ume_db, app_db):
    username = get_jwt_identity()

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
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200


@jwt_refresh_token_required
def delete(request, ume_db, app_db):
    username = get_jwt_identity()

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
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200
