import jwt
from datetime import datetime
from datetime import timedelta
from config.configConstants import JWTConstants


class JwtTokenHelper:
    # JWT access token generation
    def JWTAccessToken(self, user_id):
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(seconds=JWTConstants.JWT_EXP_DELTA_SECONDS)
            }
            accessToken = jwt.encode(payload, JWTConstants.TOKEN_SECRET, algorithm=JWTConstants.JWT_ALGORITHM)
            return accessToken
        except Exception as e:
            return False

    # JWT refresh token generation
    def JWTRefreshToken(self, user_id):
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(seconds=JWTConstants.JWT_REF_EXP_DELTA_SECONDS)
            }
            refreshToken = jwt.encode(payload, JWTConstants.REFRESH_TOKEN_SECRET, algorithm=JWTConstants.JWT_ALGORITHM)
            return refreshToken
        except Exception as e:
            return False

    # Decode the jwt token and get the payload
    def getJWTPayload(self, token):
        try:
            payload = jwt.decode(token, JWTConstants.TOKEN_SECRET,
                                 algorithms=[JWTConstants.JWT_ALGORITHM])
            if payload:
                return payload
            else:
                return None
        except Exception as e:
            return False