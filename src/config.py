import os

ALLOWED_EXTENSIONS = {'csv', 'json'}
UPLOAD_FOLDER = 'uploads' # folder where files will be uploaded
EMAIL_KEY = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg=' # key for email verification
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') # secret key used to authenticate application, stored as env variable. On Azure it's stored as application setting
    DB_USER = os.environ.get('DB_USER') # database user name stored as env variable in Azure application setting
    DB_PASS = os.environ.get('DB_PASS') # database password stored as env variable in Azure application setting
    DB_SERVER = os.environ.get('DB_SERVER', 'wodomierze-online.database.windows.net')
    DB_NAME = os.environ.get('DB_NAME', 'smbts-wodomierze-online')
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{DB_USER}:{DB_PASS}@{DB_SERVER}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server' #connection string for SQL server provided by SQL server

    EMITEL_USER = os.environ.get('DB_USER')
    EMITEL_PASS = os.environ.get('EMITEL_PASS')
    EMITEL_SERVER = os.environ.get('EMITEL_SERVER', 'dev-smartbits-db-server.database.windows.net')
    EMITEL_NAME = os.environ.get('EMITEL_NAME', 'dev-liczniki-db')

    #SQLALCHEMY_BINDS = {
        #'emitel_db': f'mssql+pyodbc://{EMITEL_USER}:{EMITEL_PASS}@{EMITEL_SERVER}/{EMITEL_NAME}?driver=ODBC+Driver+18+for+SQL+Server'
    #}