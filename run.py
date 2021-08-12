from flask import Flask, request, jsonify
from flask_cors import CORS
from src.resources.db_base import DBBase
from config import config
from src.resources.endpoint import EndPoint
from flask_jwt_extended import JWTManager
from utils.exception import GenericException

app = Flask(__name__)

cors = CORS(app)
app.config['JWT_SECRET_KEY'] = config['jwt']['secret_key']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config['jwt']['exp_sec_access']
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = config['jwt']['exp_sec_refresh']
app.config['JWT_ALGORITHM'] = config['jwt']['algorithm']

jwt = JWTManager(app)


def check_connections(db_instance):
    try:
        if db_instance._con.open is not True:
            db_instance._connect_db()

        cursor = db_instance._con.cursor()
        cursor.execute('SELECT NOW()')
    except:
        raise GenericException(
            'Bağlantı hatası, lütfen daha sonra tekrar deneyiniz',
            408
        )


@app.route('/api/v1/<segment>', defaults={'id': None}, methods=['GET'])
@app.route('/api/v1/<segment>/<id>', methods=['GET'])
def do_operation_get(segment, id):
    ume_db = DBBase.get_instance(**config['ume_db'])
    app_db = DBBase.get_instance(**config['app_db'])

    check_connections(ume_db)
    check_connections(app_db)
    json_ret = EndPoint.do_operation(segment,
                                     request,
                                     ume_db,
                                     app_db)
    DBBase.refresh()
    return json_ret


@app.route('/api/v1/<segment>', defaults={'id': None}, methods=['POST'])
@app.route('/api/v1/<segment>/<id>', methods=['POST'])
def do_operation_post(segment, id):
    ume_db = DBBase.get_instance(**config['ume_db'])
    app_db = DBBase.get_instance(**config['app_db'])

    check_connections(ume_db)
    check_connections(app_db)
    json_ret = EndPoint.do_operation(segment,
                                     request,
                                     ume_db,
                                     app_db)
    DBBase.refresh()
    return json_ret


@app.errorhandler(GenericException)
def do_handle_error(error):
    json_ret = error.message, error.status_code
    DBBase.refresh()
    return json_ret


if __name__ == '__main__':
    app.run(debug=True)
