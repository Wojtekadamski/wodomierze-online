import os
from urllib.parse import quote_plus

SQL_ADMIN_CREDENCIALS = ['adm123453324@gmaill.com', 'admin']
SQL_USER_CREDENTIALS = ['user@gmail.com', 'user']
ALLOWED_EXTENSIONS = {'csv', 'json'}
UPLOAD_FOLDER = 'uploads'
EMAIL_KEY = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
class Config(object):
    SECRET_KEY = 'RBrOvJOwFasCw0DXazq7BNB2VST5c38B'
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    #DB_USER = 'develop'
    #DB_PASS = 'fy8wzpf7HN'
    DB_SERVER = os.environ.get('DB_SERVER', 'wodomierze-online.database.windows.net')
    DB_NAME = os.environ.get('DB_NAME', 'smbts-wodomierze-online')

    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_SERVER}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server'
    #SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://develop:fy8wzpf7HN@wodomierze-online.database.windows.net:1433/smbts-wodomierze-online?driver=ODBC+Driver+18+for+SQL+Server'
