from flask_jwt_extended import (
    jwt_refresh_token_required)
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
def get_reports(request, app_db, ume_db):
    try:
        data = request.data
        parsed = json.loads(data)

        try:
            LIFNRS = parsed['DATA']['LIFNR']
            BOSLIFNR = []
            for LIFNR in LIFNRS:
                deneme = {'LIFNR': LIFNR}
                BOSLIFNR.append(deneme)
            parsed['DATA']['LIFNR'] = BOSLIFNR
        except:
            pass

        try:
            MATNRS = parsed['DATA']['MATNR']
            BOSMATNR = []
            for MATNR in MATNRS:
                deneme = {'MATNR': MATNR}
                BOSMATNR.append(deneme)
            parsed['DATA']['MATNR'] = BOSMATNR
        except:
            pass

        try:
            EBELNS = parsed['DATA']['EBELN']
            BOSEBELN = []
            for EBELN in EBELNS:
                deneme = {'EBELN': EBELN}
                BOSEBELN.append(deneme)
            parsed['DATA']['EBELN'] = BOSEBELN
        except:
            pass

        r = requests.post(host + 'reports' + client,
                          data=json.dumps({'OUT': parsed['DATA']}), verify=False)
        parsedSapData = json.loads(r.content)
        sentData = parsedSapData['OUT']

        ret = {
            'reports': sentData,
        }

        return jsonify(ret), 200

    except:
        raise GenericException(
            "Raporlar getirilirken bir sorunla karşılaşıldı!", 408)


@jwt_refresh_token_required
@Token.check_refresh
def find_po(request, app_db, ume_db):
    try:
        data = request.data
        parsed = json.loads(data)

        try:
            LIFNRS = parsed['DATA']['LIFNR']
            BOSLIFNR = []
            for LIFNR in LIFNRS:
                deneme = {'LIFNR': LIFNR}
                BOSLIFNR.append(deneme)
            parsed['DATA']['LIFNR'] = BOSLIFNR
        except:
            pass

        try:
            EKGRPS = parsed['DATA']['EKGRP']
            BOSEKGRP = []
            for EKGRP in EKGRPS:
                deneme = {'EKGRP': EKGRP}
                BOSEKGRP.append(deneme)
            parsed['DATA']['EKGRP'] = BOSEKGRP
        except:
            pass

        try:
            EBELPS = parsed['DATA']['EBELP']
            BOSEBELP = []
            for EBELP in EBELPS:
                deneme = {'EBELP': EBELP}
                BOSEBELP.append(deneme)
            parsed['DATA']['EBELP'] = BOSEBELP
        except:
            pass

        try:
            WERKSS = parsed['DATA']['WERKS']
            BOSWERKS = []
            for WERKS in WERKSS:
                deneme = {'WERKS': WERKS}
                BOSWERKS.append(deneme)
            parsed['DATA']['WERKS'] = BOSWERKS
        except:
            pass

        try:
            MATNRS = parsed['DATA']['MATNR']
            BOSMATNR = []
            for MATNR in MATNRS:
                deneme = {'MATNR': MATNR}
                BOSMATNR.append(deneme)
            parsed['DATA']['MATNR'] = BOSMATNR
        except:
            pass

        try:
            EBELNS = parsed['DATA']['EBELN']
            BOSEBELN = []
            for EBELN in EBELNS:
                deneme = {'EBELN': EBELN}
                BOSEBELN.append(deneme)
            parsed['DATA']['EBELN'] = BOSEBELN
        except:
            pass

        r = requests.post(host + 'find_po' + client,
                          data=json.dumps({'OUT': parsed['DATA']}), verify=False)
        parsedSapData = json.loads(r.content)
        sentData = parsedSapData['OUT']

        ret = {
            'findPo': sentData,
        }

        return jsonify(ret), 200

    except:
        raise GenericException(
            "Siparişleriniz bulunurken bir sorunla karşılaşıldı!", 408)
