from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity)
from utils.exception import GenericException
import json
from flask import jsonify
import datetime


@jwt_refresh_token_required
def refresh():
    username = get_jwt_identity()
    try:
        ret = {
            'refresh_token': create_refresh_token(identity=username),
        }
        return jsonify(ret), 200
    except:
        raise GenericException("Giriş işleminde bir hata ile karşılaşıldı !", 408)