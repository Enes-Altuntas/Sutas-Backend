from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity)
from utils.exception import GenericException
import json
from flask import jsonify
from datetime import datetime as dt
import requests
from base64 import b64encode
from base64 import b64decode
from config import config

host = config['host']


@jwt_refresh_token_required
def get_single(request, app_db, ume_db):
    try:
        data = request.data
        parsed = json.loads(data)
        username = get_jwt_identity()
        sup_id = parsed['sup_id']

        r = requests.get(host + 'sup_list',
                         params={'sup_id': sup_id}, verify=False)
        parsedSapData = json.loads(r.content)
        sentData = parsedSapData['OUT']

        attaches = app_db.get_ven_attach(parsed['sup_id'])
        for attach in attaches:
            attach['data_content'] = b64encode(
                attach['data_content']).decode('utf-8')

        for attach in attaches:
            date1 = dt.strptime(attach['date'], "%d/%m/%Y")
            date2 = dt.now()
            if date1 < date2:
                app_db.delete_ven_attach(attach['attach_id'])

        attaches = app_db.get_ven_attach(parsed['sup_id'])
        for attach in attaches:
            attach['data_content'] = b64encode(
                attach['data_content']).decode('utf-8')

        ret = {
            'vendor_info': sentData,
            'vendor_attachs': attaches,
            'refresh_token': create_refresh_token(identity=username)
        }

        return jsonify(ret), 200

    except:
        raise GenericException(
            "Tedarikçi bilgileri görüntülenirken bir sorunla karşılaşıldı!", 408)


@jwt_refresh_token_required
def get_list(request, app_db, ume_db):
    try:
        username = get_jwt_identity()
        user_type = ume_db.get_user_info(username)[0]['user_type']

        if user_type == 'PUR' or user_type == 'QTY':

            lifnrs = ume_db.get_user_sys_ids()
            for lifnr in lifnrs:
                lifnr['LIFNR'] = lifnr['user_sys_id']
            r = requests.get(host + 'sup_list', data=json.dumps({
                'LIFNR': lifnrs}), verify=False)
            parsedSapData = json.loads(r.content)
            sentData = parsedSapData['OUT']

            ret = {
                'vendor_list': sentData,
                'refresh_token': create_refresh_token(identity=username)
            }
            return jsonify(ret), 200

        else:
            raise GenericException(
                "Tedarikçi listesini görmek için yetkiniz bulunmamaktadır.", 403)

    except:
        raise GenericException(
            "Tedarikçi listesi görüntülenirken bir sorunla karşılaşıldı!", 408)


@jwt_refresh_token_required
def revUpdate(request, app_db, ume_db):
    # Request datasının çekilip parse edilmesi
    username = get_jwt_identity()
    data = request.data
    parsed = json.loads(data)
    sapMsg = []

    # Yeni bilgilerin gönderilmesi
    try:
        parsed['OUT'] = parsed['REV_INFO']
        lifnrs = ume_db.get_user_sys_ids()
        for lifnr in lifnrs:
            lifnr['LIFNR'] = lifnr['user_sys_id']
        r = requests.post(host + 'sup_list',
                          data=json.dumps({
                              'OUT': parsed['REV_INFO']
                          }),
                          verify=False)
        parsedSapData = json.loads(r.content)
        sapMsg = parsedSapData['OUT']

    except:
        raise GenericException(
            "Tedarikçi bilgileri güncellenirken bir sorunla karşılaşıldı!",
            408)

    # Tedarikçi bilgilerinin gösterilmesi
    try:
        lifnrs = ume_db.get_user_sys_ids()
        for lifnr in lifnrs:
            lifnr['LIFNR'] = lifnr['user_sys_id']
        r = requests.get(host + 'sup_list',
                         params={'sup_id': parsed['sup_id']}, verify=False)
        parsedSapData = json.loads(r.content)
        sentData = parsedSapData['OUT']
    except:
        raise GenericException(
            "Tedarikçi bilgileri görüntülenirken bir sorunla karşılaşıldı!",
            408)

    ret = {
        'vendor_info': sentData,
        'sapMsg': sapMsg,
        'refresh_token': create_refresh_token(identity=username)
    }

    return jsonify(ret), 200


@jwt_refresh_token_required
def perUpdate(request, app_db, ume_db):
    # Request datasının çekilip parse edilmesi
    data = request.data
    parsed = json.loads(data)
    username = get_jwt_identity()
    sapMsg = []

    # Yeni bilgilerin gönderilmesi
    try:
        index = parsed['INDEX']
        parsed['DATA']['RESP_PERS'][index]['APPR_MOBIL_TEL'] = parsed['NDATA']['mobil']
        parsed['DATA']['RESP_PERS'][index]['APPR_SMTP_ADDR'] = parsed['NDATA']['email']
        parsed['DATA']['RESP_PERS'][index]['APPR_TELF1'] = parsed['NDATA']['telf']
        parsed['DATA']['RESP_PERS'][index]['APPR_NAME1'] = parsed['NDATA']['name1']
        parsed['DATA']['RESP_PERS'][index]['APPR_NAMEV'] = parsed['NDATA']['namev']

        lifnrs = ume_db.get_user_sys_ids()
        for lifnr in lifnrs:
            lifnr['LIFNR'] = lifnr['user_sys_id']
        r = requests.post(host + 'sup_list',
                          data=json.dumps({'OUT': parsed['DATA']}), verify=False)
        parsedSapData = json.loads(r.content)
        sapMsg = parsedSapData['OUT']

    except:
        raise GenericException(
            "Tedarikçi bilgileri güncellenirken bir sorunla karşılaşıldı!",
            408)

    # Tedarikçi bilgilerinin gösterilmesi
    try:
        lifnrs = ume_db.get_user_sys_ids()
        for lifnr in lifnrs:
            lifnr['LIFNR'] = lifnr['user_sys_id']
        r = requests.get(host + 'sup_list',
                         params={'sup_id': parsed['sup_id']}, verify=False)
        parsedSapData = json.loads(r.content)
        sentData = parsedSapData['OUT']
    except:
        raise GenericException(
            "Tedarikçi bilgileri görüntülenirken bir sorunla karşılaşıldı!",
            408)

    ret = {
        'vendor_info': sentData,
        'sapMsg': sapMsg,
        'refresh_token': create_refresh_token(identity=username)
    }

    return jsonify(ret), 200


@jwt_refresh_token_required
def post_attach(request, app_db, ume_db):
    try:
        data = request.data
        parsed = json.loads(data)
        username = get_jwt_identity()
        attach = parsed['file'][0]
        attach['type'] = attach['content'].split(',')[0]
        attach['content'] = b64decode(attach['content'].split(',')[1])
        attach['sup_id'] = parsed['sup_id']
        attach['doc_type'] = parsed['doc_type']
        attach['date'] = parsed['date']

        ekler = app_db.control_ven_attach(parsed['sup_id'], parsed['doc_type'])
        if len(ekler) > 0:
            upEkler = []
            for ek in ekler:
                if parsed['doc_type'] == ek['doc_type']:
                    upEkler = ek
            app_db.update_ven_attach(attach, upEkler['attach_id'])
        else:
            app_db.post_ven_attach(attach)

    except:
        raise GenericException("Ekler yollanırken bir hata oluştu !", 408)

    try:
        attaches = app_db.get_ven_attach(parsed['sup_id'])
        for attach in attaches:
            attach['data_content'] = b64encode(
                attach['data_content']).decode('utf-8')

        for attach in attaches:
            date1 = dt.strptime(attach['date'], "%d/%m/%Y")
            date2 = dt.now()
            if date1 < date2:
                app_db.delete_ven_attach(attach['attach_id'])

        attaches = app_db.get_ven_attach(parsed['sup_id'])
        for attach in attaches:
            attach['data_content'] = b64encode(
                attach['data_content']).decode('utf-8')

    except:
        raise GenericException("Ekler çekilirken bir hata oluştu !", 408)

    ret = {
        'vendor_attachs': attaches,
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200


@jwt_refresh_token_required
def del_attach(request, app_db, ume_db):
    try:
        data = request.data
        parsed = json.loads(data)
        username = get_jwt_identity()
        app_db.del_v_attach(parsed['file'])
        attaches = app_db.get_ven_attach(parsed['sup_id'])
        for attach in attaches:
            attach['data_content'] = b64encode(
                attach['data_content']).decode('utf-8')

        for attach in attaches:
            date1 = dt.strptime(attach['date'], "%d/%m/%Y")
            date2 = dt.now()
            if date1 < date2:
                app_db.delete_ven_attach(attach['attach_id'])

        attaches = app_db.get_ven_attach(parsed['sup_id'])
        for attach in attaches:
            attach['data_content'] = b64encode(
                attach['data_content']).decode('utf-8')
        
        ret = {
        'vendor_attachs': attaches,
        'refresh_token': create_refresh_token(identity=username)
        }
        return jsonify(ret), 200


    except:
        raise GenericException("Ek silinirken bir hata oluştu !", 408)


@jwt_refresh_token_required
def post_approve(request, app_db, ume_db):
    try:
        data = request.data
        parsed = json.loads(data)
        username = get_jwt_identity()
        action = parsed['ACTION']
        sapMsg = []
        sentData = []

        lifnrs = ume_db.get_user_sys_ids()
        for lifnr in lifnrs:
            lifnr['LIFNR'] = lifnr['user_sys_id']
        r = requests.post(host + 'sup_list', params={
            'action': action}, data=json.dumps({'OUT': parsed['DATA']}), verify=False)
        parsedSapData = json.loads(r.content)
        sapMsg = parsedSapData['OUT']

        username = get_jwt_identity()
        user_type = ume_db.get_user_info(username)[0]['user_type']

        if user_type == 'PUR' or user_type == 'QTY':
            lifnrs = ume_db.get_user_sys_ids()
            for lifnr in lifnrs:
                lifnr['LIFNR'] = lifnr['user_sys_id']
            r = requests.get(host + 'sup_list', data=json.dumps({
                'LIFNR': lifnrs}), verify=False)
            parsedSapData = json.loads(r.content)
            sentData = parsedSapData['OUT']

        ret = {
            'vendor_list': sentData,
            'sapMsg': sapMsg,
            'refresh_token': create_refresh_token(identity=username)
        }

    except:
        raise GenericException(
            "Tedarikçi listesi çekilirken bir hata oluştu !", 408)

    return jsonify(ret), 200
