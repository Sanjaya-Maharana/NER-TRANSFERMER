import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def decode_jwt_token(token: str):
    try:
        decoded_token = jwt.decode(token, ADMIN_SECRET_JWT_TOKEN, algorithms=[JWT_ENCODE_ALGO])
        return decoded_token
    except ExpiredSignatureError:
        return {"error": "Token has expired"}
    except InvalidTokenError:
        return {"error": "Invalid token"}
    except Exception:
        try:
            decoded_token = jwt.decode(token, JWT_USER_SECRET_KEY, algorithms=[JWT_ENCODE_ALGO])
            return decoded_token
        except ExpiredSignatureError:
            return {"error": "Token has expired"}
        except InvalidTokenError:
            return {"error": "Invalid token"}
        except Exception as e:
            return {"error": str(e)}
