from flask import Flask
from flask_migrate import Migrate

from src.config import Config
from src.models import db, create_admin, login_manager, create_user_test
from src.routes import main_routes

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.config.from_object(Config)
migrate = Migrate(app, db)
db.init_app(app)
with app.app_context():
    db.create_all()
    create_admin()
    create_user_test()
    # create_app()
app.register_blueprint(main_routes, url_prefix='/')
login_manager.init_app(app)



if __name__ == '__main__':
    app.run()
