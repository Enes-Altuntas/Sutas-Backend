from flask_jwt_extended import (
    jwt_refresh_token_required,
    get_jwt_identity)
from utils.exception import GenericException
import json
from flask import jsonify
from base64 import b64encode
from base64 import b64decode
from collections import defaultdict
from utils.token import Token


@jwt_refresh_token_required
@Token.check_refresh
def get_anounce(request, app_db, ume_db):
    try:
        username = get_jwt_identity()
        user_info = ume_db.get_user_info(username)

        if user_info[0]['user_type'] == 'SUP':
            anounces = app_db.get_anounces(user_info[0]['user_sys_id'])
            ret = {
                'anounces': anounces,
            }

        else:
            anounces = app_db.get_anounces_all()
            groups = defaultdict(list)
            for obj in anounces:
                groups[obj['anounce']].append(obj)
            new_list = list(groups.values())
            kim = []
            empty = []
            for item in new_list:
                if len(item) > 1:
                    for a in item:
                        kim.append(a['who'])
                    item[0]['who'] = kim
                    empty.append(item[0])
                elif len(item) == 1:
                    empty.append(item[0])
            ret = {
                'anounces': empty,
            }

        return jsonify(ret), 200

    except:
        raise GenericException(
            "Duyurular sistemden çekilirken bir hata ile karşılaşıldı !", 408)


@jwt_refresh_token_required
@Token.check_refresh
def send_anounce(request, app_db, ume_db):
    username = get_jwt_identity()
    user_info = ume_db.get_user_info(username)
    data = request.data
    parsed = json.loads(data)
    try:
        if user_info[0]['user_type'] == 'PUR':
            for who in parsed['who']:
                app_db.add_anounce(parsed, who)
    except:
        raise GenericException(
            "Anons yaratmak için yetkiniz yoktur !", 408)

    anounces = app_db.get_anounces_all()
    groups = defaultdict(list)
    for obj in anounces:
        groups[obj['anounce']].append(obj)
    new_list = list(groups.values())
    kim = []
    empty = []
    for item in new_list:
        if len(item) > 1:
            for a in item:
                kim.append(a['who'])
            item[0]['who'] = kim
            empty.append(item[0])
        elif len(item) == 1:
            empty.append(item[0])
    ret = {
        'anounces': empty,
    }

    return jsonify(ret), 200


@jwt_refresh_token_required
@Token.check_refresh
def del_anounce(request, app_db, ume_db):
    username = get_jwt_identity()
    user_info = ume_db.get_user_info(username)
    data = request.data
    parsed = json.loads(data)

    try:
        if user_info[0]['user_type'] == 'PUR':
            app_db.del_anounce(parsed)
    except:
        raise GenericException(
            "Anons silmek için gerekli yetkiniz yoktur !", 408)

    anounces = app_db.get_anounces_all()
    groups = defaultdict(list)
    for obj in anounces:
        groups[obj['anounce']].append(obj)
    new_list = list(groups.values())
    kim = []
    empty = []
    for item in new_list:
        if len(item) > 1:
            for a in item:
                kim.append(a['who'])
            item[0]['who'] = kim
            empty.append(item[0])
        elif len(item) == 1:
            empty.append(item[0])
    ret = {
        'anounces': empty,
    }

    return jsonify(ret), 200


@jwt_refresh_token_required
@Token.check_refresh
def push_help_attach(request, app_db, ume_db):
    username = get_jwt_identity()
    user_info = ume_db.get_user_info(username)
    data = request.data
    parsed = json.loads(data)

    if user_info[0]['user_type'] == 'PUR':
        for file in parsed['file']:
            file['content'] = b64decode(file['content'].split(',')[1])
            app_db.push_attach(file)
    else:
        raise GenericException(
            "Ek eklemek için gerekli yetkiniz yoktur !", 408)

    attaches = app_db.get_help_attach()
    for attach in attaches:
        attach['data_content'] = b64encode(
            attach['data_content']).decode('utf-8')
    ret = {
        'attaches': attaches,
    }

    return jsonify(ret), 200


@jwt_refresh_token_required
@Token.check_refresh
def pull_help_attach(request, app_db, ume_db):
    username = get_jwt_identity()

    attaches = app_db.get_help_attach()
    for attach in attaches:
        attach['data_content'] = b64encode(
            attach['data_content']).decode('utf-8')
    ret = {
        'attaches': attaches,
    }

    return jsonify(ret), 200


@jwt_refresh_token_required
@Token.check_refresh
def del_help_attach(request, app_db, ume_db):
    username = get_jwt_identity()
    user_info = ume_db.get_user_info(username)
    data = request.data
    parsed = json.loads(data)

    if user_info[0]['user_type'] == 'PUR':
        app_db.del_attach(parsed)
    else:
        raise GenericException(
            "Ek silmek için gerekli yetkiniz yoktur !", 408)

    attaches = app_db.get_help_attach()
    for attach in attaches:
        attach['data_content'] = b64encode(
            attach['data_content']).decode('utf-8')
    ret = {
        'attaches': attaches,
    }

    return jsonify(ret), 200
