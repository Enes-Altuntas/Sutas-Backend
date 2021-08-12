from flask_jwt_extended import (
    jwt_refresh_token_required,
    get_jwt_identity)
from utils.exception import GenericException
import json
from src.resources.db_base import DBBase
from flask import jsonify
import requests
from base64 import b64encode
from base64 import b64decode
from config import config
from utils.token import Token

host = config['host']
client = config['client']


@jwt_refresh_token_required
@Token.check_refresh
def getAll(request, app_db, ume_db):

    username = get_jwt_identity()
    sentData = []
    data = request.data
    parsed = json.loads(data)
    filter = parsed['filter']
    statu = filter.replace('/po/', '')
    sup_id = ume_db.get_user_info(username)[0]['user_sys_id']
    user_type = ume_db.get_user_info(username)
    try:
        if user_type[0]['user_type'] == 'SUP':

            if statu != '21':
                r = requests.get(host + 'po_list' + client,
                                 params={'action': '2', 'statu': statu, 'sup_id': sup_id}, verify=False)
                parsedSapData = json.loads(r.content)
                sentData = parsedSapData['OUT']
            else:
                statu_onay = '02'
                statu_sevk = '05'
                r = requests.get(host + 'po_list' + client,
                                 params={'action': '2', 'statu': statu_onay, 'sup_id': sup_id}, verify=False)
                parsedSapData = json.loads(r.content)
                sentData = parsedSapData['OUT']
                parsedSapData = ''
                r = requests.get(host + 'po_list' + client,
                                 params={'action': '2', 'statu': statu_sevk, 'sup_id': sup_id}, verify=False)
                parsedSapData = json.loads(r.content)
                for parsedData in parsedSapData['OUT']:
                    sentData.append(parsedData)

        else:
            r = requests.get(host + 'po_list' + client,
                             params={'action': '1', 'statu': statu}, verify=False)
            parsedSapData = json.loads(r.content)
            sentData = parsedSapData['OUT']

        i = 0
        for data in sentData:
            i = i + 1
            data['ID'] = i
    except:
        raise GenericException(
            "Siparişler yüklenirken bir hata meydana geldi !", 408)

    if statu == '03' or statu == '07' or statu == '04' or statu == '02' or statu == '01' or statu == '21':
        revDesc = app_db.get_rev_desc()
        decDesc = app_db.get_dec_desc()
        rejDesc = app_db.get_rej_desc()
        rejPlanDesc = app_db.get_plan_rej_desc()
        for data in sentData:
            for rev in revDesc:
                if rev['po_number'] == data['EBELN']:
                    if rev['po_item'] == data['EBELP']:
                        data['revDesc'] = rev['rev_desc']
            for dec in decDesc:
                if dec['po_number'] == data['EBELN']:
                    if dec['po_item'] == data['EBELP']:
                        data['decDesc'] = dec['dec_desc']
            for rej in rejDesc:
                if rej['po_number'] == data['EBELN']:
                    if rej['po_item'] == data['EBELP']:
                        data['rejDesc'] = rej['rej_desc']
            for rejPlan in rejPlanDesc:
                if rejPlan['po_number'] == data['EBELN']:
                    if rejPlan['po_item'] == data['EBELP']:
                        data['rejPlanDesc'] = rejPlan['rej_desc']

    ret = {
        'sentData': sentData,
    }
    return jsonify(ret), 200


@jwt_refresh_token_required
@Token.check_refresh
def get_attach(request, app_db, ume_db):
    try:
        attaches = []
        sentData = []
        username = get_jwt_identity()
        data = request.data
        parsed = json.loads(data)
        r = requests.get(host + 'get_asn' + client,
                         params={'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)
        parsedSapData = json.loads(r.content)
        sentData = parsedSapData['OUT']
        parsed['EBELN'] = parsed['po_number']
        parsed['EBELP'] = parsed['po_item']
        attaches = app_db.get_po_attach(parsed)
        for attach in attaches:
            attach['data_content'] = b64encode(
                attach['data_content']).decode('utf-8')

    except:
        raise GenericException("Ekler çekilirken bir hata oluştu !", 408)

    ret = {
        'attach': attaches,
        'sentData': sentData,
    }
    return jsonify(ret), 200


def post_attach(attaches, items):
    app_db = DBBase.get_instance(**config['app_db'])
    for attach in attaches:
        attach['type'] = attach['content'].split(',')[0]
        attach['content'] = b64decode(attach['content'].split(',')[1])
        app_db.post_po_attach_item(attach)
        attach_id = app_db.get_po_attach_id(attach)
        for item in items:
            app_db.post_po_attach_header(item, attach_id)
