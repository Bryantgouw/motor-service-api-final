import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta

class AuthHandler():
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    auth_security = HTTPBearer()
    secret_key = 'SECRET'

    def encode_jwt_token(self, id_user):
        payload = {
            'expiration': datetime.utcnow() + timedelta(days=0, minutes=5),
            'issued_at': datetime.utcnow(),
            'user_id': id_user
        }

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )

    def decode_jwt_token(self, jwt_token):
        try:
            payload = jwt.decode(jwt_token, self.secret_key, algorithms=['HS256'])
            return payload['user_id']

        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail='Invalid token')
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired')
        
    def get_hashing_password(self,password):
        return self.pwd.hash(password)

    def password_verification(self, plain_password, hashed_password):
        return self.pwd.verify(plain_password, hashed_password)

    def authentication_wrapper(self, auth: HTTPAuthorizationCredentials = Security(auth_security)):
        return jwt.decode(auth.credentials, self.secret_key, algorithms=['HS256'])['user_id']