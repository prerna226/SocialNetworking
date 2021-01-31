class JWTConstants():
    JWT_ALGORITHM = 'HS256'
    JWT_EXP_DELTA_SECONDS = 864000  # valid upto 10 days
    JWT_REF_EXP_DELTA_SECONDS = 864000  # valid upto 10 days 
    TOKEN_SECRET = 'pBIR6HjuYKrtd3N6vXfKV6S6dMPOmQ-ZvFv22vEIgfrBPNWHAgVWnPNX4SczNdYRlIevkjk4JrkgTjSK7GEuAZCGxQNWsgpTToGCmjSE_U98fzubS91xZi7onSupY3O5WhMvSgkG'
    REFRESH_TOKEN_SECRET = 'pBIR6HjuYKrtd3N6vXfKV6S6dMPOmQ-ZvFv22vEIgfrBPNWHAgVWnPNX4SczNdYRlIevkjk4JrkgTjSK7GEuAZCGxQNWsgpTToGCmjSE_U98fzubS91xZi7onSupY3O5WhMvSgkG'
    REFRESH_TOKEN_SALT = '9324bb32jhjhj432h23h436778678ghghjghjghhrtrt'
    FOROGOT_EXP_DELTA_SECONDS = 3600


class passwordSalt():
    SALT = '0b970daf42db46feac8354daa353110f'  # uuid.uuid4().hex




