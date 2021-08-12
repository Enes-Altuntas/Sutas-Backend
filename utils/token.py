from functools import wraps
from utils.exception import GenericException
from flask_jwt_extended import get_jwt_identity


class Token():

    def check_refresh(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            authentication = args[0].headers.environ["HTTP_AUTHORIZATION"].split(
                ' ')
            token = authentication[1]
            username = get_jwt_identity()
            token_db = args[2].get_token(username)
            if(token_db[0]["refresh_token"] == token):
                return fn(*args, **kwargs)
            else:
                raise GenericException(
                    "Başka bir tarayıcıdan açılmış olan bir oturumunuz var !", 401)
        return wrapper
