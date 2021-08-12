from flask_jwt_extended import (
    jwt_refresh_token_required,
    get_jwt_identity)
import json
import src.resources.endpoint.po as RequestedResource
from flask import jsonify
import requests
from config import config
from utils.token import Token

host = config['host']
client = config['client']


@jwt_refresh_token_required
@Token.check_refresh
def update_statu(request, app_db, ume_db):
    username = get_jwt_identity()
    data = request.data
    parsed = json.loads(data)
    filter = parsed['filter']
    statu = filter.replace('/po/', '')
    sapMsg = []

    if statu == '01':
        if parsed['onay'] == 'false':
            # ****************Tedarikçi Revizyon Talebi************************
            app_db.del_plan_rej_desc(parsed)
            parsed['zrev_deliv'] = parsed['zrev_deliv'].replace('-', '')
            app_db.insert_rev_desc(parsed)
            requests.post(host + 'po_list' + client, params={
                'action': '2', 'po_number': parsed['po_number'], 'po_item': parsed['po_item'], 'zrev_quan': parsed['zrev_quan'], 'zrev_deliv': parsed['zrev_deliv']}, verify=False)

        elif parsed['onay'] == 'true':
            # *****************Tedarikçi Sipariş Onayı**************************
            app_db.del_plan_rej_desc(parsed)
            requests.post(host + 'po_list' + client, params={
                'action': '1', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)

    # Tedarikçi Sütaş Revizyon Kabulü ve Reddi
    elif statu == '08':
        if parsed['onay'] == 'true':
            requests.post(host + 'po_list' + client, params={
                'action': '12', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)

        elif parsed['onay'] == 'false':
            app_db.insert_rej_desc(parsed)
            r = requests.post(host + 'po_list' + client, params={
                'action': '13', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)
            parsedSapData = json.loads(r.content)
            sapMsg = parsedSapData['OUT']

    elif statu == '07':
        if parsed['onay'] == 'true':
            # **************************Satın Alma Revizyon Reddi***********************************
            app_db.del_rev_desc(parsed)
            app_db.del_dec_desc(parsed)
            requests.post(host + 'po_list' + client, params={
                'action': '8', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)

        elif parsed['onay'] == 'false':
            # **************************Satın Alma Siapriş Reddi************************************
            app_db.del_dec_desc(parsed)
            r = requests.post(host + 'po_list' + client, params={
                'action': '9', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)
            parsedSapData = json.loads(r.content)
            sapMsg = parsedSapData['OUT']

    # Tedarikçi Sütaş iptal Kabulü ve Reddi
    elif statu == '06':
        if parsed['onay'] == 'true':
            r = requests.post(host + 'po_list' + client, params={
                'action': '11', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)
            parsedSapData = json.loads(r.content)
            sapMsg = parsedSapData['OUT']
        elif parsed['onay'] == 'false':
            requests.post(host + 'po_list' + client, params={
                'action': '10', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)

    elif statu == '03':
        if parsed['onay'] == 'true':
            # ****************************Planlamacının Revizyonu Kabul Etmesi******************************************
            app_db.del_rev_desc(parsed)
            r = requests.post(host + 'po_list' + client, params={
                'action': '4', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)
            parsedSapData = json.loads(r.content)
            sapMsg = parsedSapData['OUT']
        elif parsed['onay'] == 'false':
            # ****************************Planlamacının Revizyonu Reddetmesi*********************************************
            app_db.del_rev_desc(parsed)
            app_db.insert_plan_rej_desc(parsed)
            requests.post(host + 'po_list' + client, params={
                'action': '5', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)

        elif parsed['onay'] == 'dunno':
            # ****************************Planlamacının Satın Alma Kararına Yollaması*************************************
            app_db.insert_dec_desc(parsed)
            requests.post(host + 'po_list' + client, params={
                'action': '6', 'po_number': parsed['po_number'], 'po_item': parsed['po_item']}, verify=False)

    # Sevk durumu
    elif statu == '02':
        # Onaylı siparişin sevk edilmesi
        if parsed['onay'] == 'true':
            if 'PLATE_NO' not in parsed or parsed['PLATE_NO'] is None or parsed['PLATE_NO'] == '':
                parsed['PLATE_NO'] = '34AA1234'

            if 'DRIVER_NAME' not in parsed or parsed['DRIVER_NAME'] is None or parsed['DRIVER_NAME'] == '':
                if parsed['ARAC_TIPI'] == '03':
                    parsed['DRIVER_NAME'] = 'Kargo'
                elif parsed['ARAC_TIPI'] == '02':
                    parsed['DRIVER_NAME'] = 'Sutas'

            if 'PHONE_NUMBER' not in parsed or parsed['PHONE_NUMBER'] is None or parsed['PHONE_NUMBER'] == '':
                parsed['PHONE_NUMBER'] = '5556667788'

            r = requests.post(host + 'po_list' + client, params={
                'action': '7', 'sup_id': parsed['sup_id']}, data=json.dumps({'OUT': parsed}), verify=False)
            parsedSapData = json.loads(r.content)
            sapMsg = parsedSapData['OUT']
            if not sapMsg:
                RequestedResource.post_attach(parsed['file'], parsed['ITEMS'])
            else:
                for msg in sapMsg:
                    if msg['TYPE'] != 'E':
                        RequestedResource.post_attach(
                            parsed['file'], parsed['ITEMS'])
                        break
                    else:
                        break

        # Onaylı Sipariş için revizyon talebi
        elif parsed['onay'] == 'false':
            app_db.del_rej_desc(parsed)
            parsed['zrev_deliv'] = parsed['zrev_deliv'].replace('-', '')
            app_db.insert_rev_desc(parsed)
            requests.post(host + 'po_list' + client, params={
                'action': '3', 'po_number': parsed['po_number'], 'po_item': parsed['po_item'], 'zrev_quan': parsed['zrev_quan'], 'zrev_deliv': parsed['zrev_deliv']}, verify=False)

    # Parçalı sevk üzerinden sevk
    elif statu == '05':
        if parsed['onay'] == 'true':
            if 'PLATE_NO' not in parsed or parsed['PLATE_NO'] is None or parsed['PLATE_NO'] == '':
                parsed['PLATE_NO'] = '34AA1234'

            if 'DRIVER_NAME' not in parsed or parsed['DRIVER_NAME'] is None or parsed['DRIVER_NAME'] == '':
                if parsed['ARAC_TIPI'] == '03':
                    parsed['DRIVER_NAME'] = 'Kargo'
                elif parsed['ARAC_TIPI'] == '02':
                    parsed['DRIVER_NAME'] = 'Sutas'

            if 'PHONE_NUMBER' not in parsed or parsed['PHONE_NUMBER'] is None or parsed['PHONE_NUMBER'] == '':
                parsed['PHONE_NUMBER'] = '5556667788'

            r = requests.post(host + 'po_list' + client, params={
                'action': '7', 'sup_id': parsed['sup_id']}, data=json.dumps({'OUT': parsed}), verify=False)
            parsedSapData = json.loads(r.content)
            sapMsg = parsedSapData['OUT']
            if not sapMsg:
                RequestedResource.post_attach(parsed['file'], parsed['ITEMS'])
            else:
                for msg in sapMsg:
                    if msg['TYPE'] != 'E':
                        RequestedResource.post_attach(
                            parsed['file'], parsed['ITEMS'])
                        break
                    else:
                        break

    # Yeni sevk üzerinden sevk
    elif statu == '21':
        if parsed['onay'] == 'true':
            if 'PLATE_NO' not in parsed or parsed['PLATE_NO'] is None or parsed['PLATE_NO'] == '':
                parsed['PLATE_NO'] = '34AA1234'

            if 'DRIVER_NAME' not in parsed or parsed['DRIVER_NAME'] is None or parsed['DRIVER_NAME'] == '':
                if parsed['ARAC_TIPI'] == '03':
                    parsed['DRIVER_NAME'] = 'Kargo'
                elif parsed['ARAC_TIPI'] == '02':
                    parsed['DRIVER_NAME'] = 'Sutas'

            if 'PHONE_NUMBER' not in parsed or parsed['PHONE_NUMBER'] is None or parsed['PHONE_NUMBER'] == '':
                parsed['PHONE_NUMBER'] = '5556667788'

            r = requests.post(host + 'po_list' + client, params={
                'action': '7', 'sup_id': parsed['sup_id']}, data=json.dumps({'OUT': parsed}), verify=False)
            parsedSapData = json.loads(r.content)
            sapMsg = parsedSapData['OUT']
            if not sapMsg:
                RequestedResource.post_attach(parsed['file'], parsed['ITEMS'])
            else:
                for msg in sapMsg:
                    if msg['TYPE'] != 'E':
                        RequestedResource.post_attach(
                            parsed['file'], parsed['ITEMS'])
                        break
                    else:
                        break

    # Po Güncel Liste Çekilmesi
    user_type = ume_db.get_user_info(username)
    if user_type[0]['user_type'] == 'SUP':
        if statu != '21':
            r = requests.get(host + 'po_list' + client,
                             params={'action': '2', 'statu': statu, 'sup_id': parsed['sup_id']}, verify=False)
            parsedSapData = json.loads(r.content)
            sentData = parsedSapData['OUT']
        else:
            statu_onay = '02'
            statu_sevk = '05'
            r = requests.get(host + 'po_list' + client,
                             params={'action': '2', 'statu': statu_onay, 'sup_id': parsed['sup_id']}, verify=False)
            parsedSapData = json.loads(r.content)
            sentData = parsedSapData['OUT']
            parsedSapData = ''
            r = requests.get(host + 'po_list' + client,
                             params={'action': '2', 'statu': statu_sevk, 'sup_id': parsed['sup_id']}, verify=False)
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

    ret = {
        'sentData': sentData,
        'sapMsg': sapMsg,
    }
    return jsonify(ret), 200
