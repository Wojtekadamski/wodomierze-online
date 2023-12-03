import os
from urllib.parse import quote_plus

ALLOWED_EXTENSIONS = {'csv', 'json'}
UPLOAD_FOLDER = 'uploads'
EMAIL_KEY = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_SERVER = os.environ.get('DB_SERVER', 'wodomierze-online.database.windows.net')
    DB_NAME = os.environ.get('DB_NAME', 'smbts-wodomierze-online')

    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_SERVER}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server'