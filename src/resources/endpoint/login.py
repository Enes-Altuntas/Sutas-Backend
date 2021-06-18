from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, decode_token)
from utils.exception import GenericException
import json
from flask import jsonify
import datetime
import random
import string
import requests
import jwt
from config import config

host = config['host']
client = config['client']
secret = config['jwt']['secret_key']


def login(request, ume_db):

    data = request.data
    parsed = json.loads(data)
    username = parsed['username']
    password = parsed['password']
    try:
        if (ume_db.get_user_info(username)[0]['password'] == password):
            ret = {
                'refresh_token': create_refresh_token(identity=username),
            }
        return jsonify(ret), 200
    except:
        raise GenericException("Kullanıcı adı veya şifre hatalı !", 403)


def forget(request, ume_db):
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
def changePass(request, ume_db):
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
