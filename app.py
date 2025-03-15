from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from models import db, User
from blueprints.tasks import tasks
from blueprints.auth import auth, login_manager
from blueprints.users import users
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager.init_app(app)
bootstrap = Bootstrap(app)

app.register_blueprint(auth)
app.register_blueprint(tasks)
app.register_blueprint(users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password_hash=generate_password_hash('admin'), role='admin')
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)