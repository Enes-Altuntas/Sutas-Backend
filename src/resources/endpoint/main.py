from functools import wraps
from flask_jwt_extended import (
    jwt_refresh_token_required,
    get_jwt_identity)
from utils.exception import GenericException
from utils.token import Token
import src.resources.endpoint.anounce as anounce
import json
import requests
from flask import jsonify
from datetime import datetime, timedelta
from config import config

host = config['host']
client = config['client']


def get_row(section):
    return section.get('row')


@jwt_refresh_token_required
@Token.check_refresh
def getAll(request, app_db, ume_db):
    try:
        badge = []
        msgParams = []

        # Token'dan username'in alınıp modüllerin çekilmesi

        username = get_jwt_identity()
        modules = ume_db.get_main_menu(username)

        # User numaralarının çekilmesi

        user_sys_ids = ume_db.get_ids()
        for user in user_sys_ids:
            user['complete'] = user['company'] + " - "+user['user_sys_id']

        # Üretim Yerlerinin Çekilmesi

        r = requests.get(host + 'get_werks' + client,
                         verify=False)
        parsedSapData = json.loads(r.content)
        werksData = parsedSapData['OUT']
        for werks in werksData:
            werks['complete'] = werks['NAME1'] + " - " + werks['WERKS']

        # Anonsların çekilmesi

        user_info = ume_db.get_user_info(username)
        if user_info[0]['user_type'] == 'SUP':
            anounces = app_db.get_anounces(user_info[0]['user_sys_id'])
            adet = len(anounces)
            if adet > 0:
                badgeBody = {}
                badgeBody['id'] = user_info[0]['user_sys_id']
                badgeBody['message'] = str(
                    adet) + ' adet duyurunuz bulunmaktadır.'
                badgeBody['to'] = '/duyurular'
                badge.append(badgeBody)

        else:
            anounces = app_db.get_anounces_all()

        # Tedarikçi reminder

        if user_info[0]['user_type'] == 'SUP':
            attaches = app_db.get_ven_attach(user_info[0]['user_sys_id'])
            for attach in attaches:
                attachDate = datetime.strptime(
                    attach['date'], "%d/%m/%Y") - timedelta(days=7)
                present = datetime.now()
                if present >= attachDate:
                    msgParams.append(attach['doc_type'])
            for params in msgParams:
                badgeBody = {}
                badgeBody['id'] = user_info[0]['user_sys_id']
                badgeBody['message'] = params + \
                    ' türündeki belgenizin geçerlilik süresinin dolmasına 7 günden az kalmıştır.'
                badgeBody['to'] = '/sup/' + user_info[0]['user_sys_id']
                badge.append(badgeBody)

        # Satın Almacı bilgi revizyonu reminder

        if user_info[0]['user_type'] == 'PUR' or user_info[0]['user_type'] == 'QTY':

            lifnrs = ume_db.get_user_sys_ids()
            for lifnr in lifnrs:
                lifnr['LIFNR'] = lifnr['user_sys_id']
            r = requests.get(host + 'sup_list', data=json.dumps({
                'LIFNR': lifnrs}), verify=False)
            parsedSapData = json.loads(r.content)
            sentData = parsedSapData['OUT']

            for data in sentData:
                if data['WAITING_APPR'] == 'X':
                    badgeBody = {}
                    badgeBody['id'] = data['LIFNR']
                    badgeBody['message'] = data['LIFNR'] + \
                        ' kodlu tedarikçiniz bilgilerinde güncelleme yapmıştır.'
                    badgeBody['to'] = '/sup'
                    badge.append(badgeBody)

        # Sipariş adetlerinin çekilmesi

        quans = []

        if user_info[0]['user_type'] == 'SUP':
            r = requests.get(host + 'log_tab_count' + client,
                             params={'sup_id': user_info[0]['user_sys_id']}, verify=False)
            parsedSapData = json.loads(r.content)
            sentData = parsedSapData['OUT']
        else:
            r = requests.get(host + 'log_tab_count' + client,
                             verify=False)
            parsedSapData = json.loads(r.content)
            sentData = parsedSapData['OUT']

        for i in range(9):
            sayi = {}
            sayi['baslik'] = '0' + str(i+1)
            sayi['id'] = '0' + str(i + 1)
            sayi['adet'] = sentData['LOG_TAB_0' + str(i+1)]
            sayi['url'] = '/po/0' + str(i+1)
            quans.append(sayi)

        quans[0]['baslik'] = 'Tedarikçi Onayı Bekleyen Siparişler'
        quans[1]['baslik'] = 'Tedarikçi Tarafından Onaylanan Siparişler'
        quans[2]['baslik'] = 'Tedarikçinin Revizyon Talebinde Bulunduğu Siparişler'
        quans[3]['baslik'] = 'Mutabakat İle İptal Edilen Siparişler'
        quans[4]['baslik'] = 'Kısmen Sevk Edilmiş Siparişler'
        quans[5]['baslik'] = 'İptal Talebinde Bulunduğumuz Siparişler'
        quans[6]['baslik'] = 'Mutabık Kalınmamış Siparişler'
        quans[7]['baslik'] = 'Revizyon Talebinde Bulunduğumuz Siparişler'
        quans[8]['baslik'] = 'Tamamı Sevk Edilmiş Siparişler'

        sayi = {}
        sayi['baslik'] = 'İade Edilen Siparişler'
        sayi['id'] = '20'
        sayi['adet'] = sentData['LOG_TAB_20']
        sayi['url'] = '/po/20'
        quans.append(sayi)

    except:
        raise GenericException("Veritabanında bir hata meydana geldi !", 408)

    try:
        admin_info = []
        users = ume_db.get_users()

        qty_count = 0
        sup_count = 0
        pla_count = 0
        pur_count = 0
        for user in users:
            if user['user_type'] == 'QTY':
                qty_count += 1
            if user['user_type'] == 'PUR':
                pur_count += 1
            if user['user_type'] == 'PLA':
                pla_count += 1
            if user['user_type'] == 'SUP':
                sup_count += 1

        admin_info_obj = {'user_role': 'Kaliteci', 'user_count': qty_count}
        admin_info.append(admin_info_obj)
        admin_info_obj = {'user_role': 'Planlamacı', 'user_count': pla_count}
        admin_info.append(admin_info_obj)
        admin_info_obj = {'user_role': 'Satınalmacı', 'user_count': pur_count}
        admin_info.append(admin_info_obj)
        admin_info_obj = {'user_role': 'Tedarikçi', 'user_count': sup_count}
        admin_info.append(admin_info_obj)

    except:
        raise GenericException(
            "Admin bilgileri çekilirken hata meydana geldi !", 408)

    ret = {
        'opened_modules': [],
        'without_sub': [],
        'user': user_sys_ids,
        'anounces': anounces,
        'quans': quans,
        'werks': werksData,
        'badge': badge,
        'admin_info': admin_info,
    }

    try:
        opened_modules = []
        module_sections = []
        for module in modules:
            if '{sup_id}' in module['url']:
                module['url'] = module['url'].replace("{sup_id}",
                                                      module['user_sys_id'])
            if(module['top_menu_id'] is None):
                opened_modules.append(module)
            else:
                module_sections.append(module)

        module_sections.sort(key=get_row)

        for opened in opened_modules:
            opened['subMenu'] = []
            for module in module_sections:
                if(opened['menu_id'] == module['top_menu_id']):
                    opened['subMenu'].append(module)
            if len(opened['subMenu']) > 0:
                ret['opened_modules'].append(opened)
            else:
                ret['without_sub'].append(opened)
    except:
        raise GenericException(
            'Menüler hazırlanırken bir hata meydana geldi !', 408)

    for quan in quans[:]:
        done = False
        for module in module_sections:
            if module['description'] == quan['baslik']:
                done = True
        if done != True:
            index = quans.index(quan)
            quans.pop(index)

    for quan in quans:
        for module in module_sections:
            if module['description'] == quan['baslik']:
                quan['row'] = module['row']
                break

    quans.sort(key=get_row)

    # İptal edilenler Satınalma Kararı ve Tamamlananların Kaldırılması
    new_quans = []
    count = 1
    for quan in quans:
        if quan['row'] == 1 or quan['row'] == 3 or quan['row'] == 4 or quan['row'] == 5 or quan['row'] == 7 or quan['row'] == 8:
            new_quans.append(quan)

    for new_quan in new_quans:
        new_quan['row'] = count
        count += 1

    ret['quans'] = new_quans

    return jsonify(ret), 200
