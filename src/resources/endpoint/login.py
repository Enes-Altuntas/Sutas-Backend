from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, decode_token)
from utils.exception import GenericException
import json
from flask import jsonify
from datetime import datetime
import requests
from config import config
from utils.token import Token

host = config['host']
client = config['client']
secret = config['jwt']['secret_key']


def login(request, app_db, ume_db):
    datetime_local = datetime.now()
    datetime_local_str = datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
    data = request.data
    parsed = json.loads(data)
    username = parsed['username']
    password = parsed['password']
    db_pass = ume_db.get_user_info(username)[0]['password']
    try:
        if (db_pass == password):
            ret = {
                'refresh_token': create_refresh_token(identity=username),
                'access_token': create_access_token(identity=username)
            }

        ume_db.set_token(
            username, ret['access_token'], ret['refresh_token'], datetime_local, datetime_local_str)
        return jsonify(ret), 200
    except:
        raise GenericException("Kullanıcı adı veya şifre hatalı !", 403)


def forget(request, app_db, ume_db):
    data = request.data
    parsed = json.loads(data)
    username = parsed['DATA']
    mail = ume_db.get_user_info(username)[0]['email']
    r = requests.post(host + 'change_pass' + client,
                      params={'mail': mail}, data=json.dumps(parsed), verify=False)
    parsedSapData = json.loads(r.content)
    sentData = parsedSapData['OUT']
    ume_db.change_pass(username, sentData)

    try:
        ret = {
            'valid': 'wait'
        }
        return jsonify(ret), 200

    except:
        raise GenericException(
            "Mail atılırken bir hata ile karşılaşıldı !", 408)


@jwt_refresh_token_required
@Token.check_refresh
def changePass(request, app_db, ume_db):
    try:
        username = get_jwt_identity()
        data = request.data
        parsed = json.loads(data)
        oldpass = parsed['DATA']['OLD_PASS']
        newpass = parsed['DATA']['NEW_PASS']

        old_password = ume_db.get_user_info(username)[0]['password']

        if old_password == oldpass:
            ume_db.change_pass(username, newpass)
            ret = {
                'valid': 'validated'
            }
        else:
            ret = {
                'valid': 'not_validated'
            }

        return jsonify(ret), 200

    except:
        raise GenericException(
            "Şifre değiştirilirken bir problem ile karşılaşıldı !", 408)
