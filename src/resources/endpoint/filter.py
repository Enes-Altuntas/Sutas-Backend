from flask_jwt_extended import (
    jwt_refresh_token_required,
    get_jwt_identity)
from utils.exception import GenericException
import json
from flask import jsonify
import requests
from config import config
from utils.token import Token

host = config['host']
client = config['client']


@jwt_refresh_token_required
@Token.check_refresh
def filterItems(request, app_db, ume_db):
    try:
        statu_onay = '02'
        statu_sevk = '05'
        filtered = []
        username = get_jwt_identity()
        data = request.data
        parsed = json.loads(data)
        route = parsed['route']
        statu = route.replace('/po/', '')
        sup_id = parsed['sup_id']
        user_type = ume_db.get_user_info(username)
        if user_type[0]['user_type'] == 'SUP':
            if statu == '21':
                r = requests.get(host + 'po_list' + client,
                                 params={'statu': statu_onay, 'sup_id': sup_id}, data=json.dumps(parsed), verify=False)
                parsedSapData = json.loads(r.content)
                sentData = parsedSapData['OUT']

                for data in sentData:
                    filtered.append(data)

                r = requests.get(host + 'po_list' + client,
                                 params={'statu': statu_sevk, 'sup_id': sup_id}, data=json.dumps(parsed), verify=False)
                parsedSapData = json.loads(r.content)
                sentData = parsedSapData['OUT']

                for data in sentData:
                    filtered.append(data)
            else:
                r = requests.get(host + 'po_list' + client,
                                 params={'statu': statu, 'sup_id': sup_id}, data=json.dumps(parsed), verify=False)
                parsedSapData = json.loads(r.content)
                sentData = parsedSapData['OUT']

                filtered = sentData
        else:
            if statu == '21':
                r = requests.get(host + 'po_list' + client,
                                 params={'statu': statu_onay}, data=json.dumps(parsed), verify=False)
                parsedSapData = json.loads(r.content)
                sentData = parsedSapData['OUT']

                for data in sentData:
                    filtered.append(data)

                r = requests.get(host + 'po_list' + client,
                                 params={'statu': statu_sevk}, data=json.dumps(parsed), verify=False)
                parsedSapData = json.loads(r.content)
                sentData = parsedSapData['OUT']

                for data in sentData:
                    filtered.append(data)
            else:
                r = requests.get(host + 'po_list' + client,
                                 params={'statu': statu}, data=json.dumps(parsed), verify=False)
                parsedSapData = json.loads(r.content)
                sentData = parsedSapData['OUT']

                filtered = sentData

        i = 0
        for data in filtered:
            i = i + 1
            data['ID'] = i

        ret = {
            'sentData': filtered,
        }
        return jsonify(ret), 200

    except:
        raise GenericException(
            "Filtreleme işlemi gerçekleştirilirken bir hata meydana gelmiştir !", 408)
