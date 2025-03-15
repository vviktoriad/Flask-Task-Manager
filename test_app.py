import pytest
from app import app, db
from models import User
from werkzeug.security import generate_password_hash
from forms import RegisterForm, LoginForm

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create database schema
            yield client
            db.session.remove()
            db.drop_all()

def test_register(client):
    test_user = User.query.filter_by(username='test_user').first()
    if test_user:
        db.session.delete(test_user)
        db.session.commit()
    response = client.post('/register', data={'username': 'test_user', 'email': 'test_user@gmail.com', 'password': 'test_user', 'confirm_password': 'test_user'}, follow_redirects=True)
    assert response.status_code == 200
    user = User.query.filter_by(username='test_user').first()
    assert user is not None

def test_register_form(client):
    form = RegisterForm()
    form.username.data = 'test_user'
    form.email.data = 'test_user@gmail.com'
    form.password.data = 'test_user'
    form.confirm_password.data = 'test_user'
    assert form.validate() == True

    form.username.data = ''
    form.email.data = 'invalid'
    form.password.data = 'test_user'
    form.confirm_password.data = 'test_user1'
    assert form.validate() == False

    assert 'This field is required.' in form.username.errors
    assert 'Invalid email address.' in form.email.errors

def test_login(client):
    response = client.post('/login', data={'username': 'test_user', 'password': 'test_user', 'remember': 'False'}, follow_redirects=True)
    assert response.status_code == 200

    response = client.post('/login', data={'username': 'nonexistent_user', 'password': 'test_user', 'remember': 'False'}, follow_redirects=True)
    assert response.status_code == 200

def test_login_invalid(client):
    response = client.post('/login', data={'username': 'test_user', 'password': 'wrong_password'}, follow_redirects=True)
    assert b'Invalid username or password' in response.data

def test_database_connection(client):
    result = db.session.query(User).all() 
    assert result is not None

def test_add_record_to_db(client):
    user = User(username='test', password_hash=generate_password_hash('test'), role='user')
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username='test').first()
    assert user is not None

def test_server_response_200(client):
    response = client.get('/login')
    print(response.data)
    assert response.status_code == 200 

def test_server_response_404(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_user_role(client):
    user = User(username='user', password_hash=generate_password_hash('user'), role='user')
    db.session.add(user)
    db.session.commit()
    response = client.post('/login', data={'username': 'user', 'password': 'user'}, follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert '_user_id' in session  # Check session to verify login
    response = client.get('/users')
    assert response.status_code == 403 #forbidden

def test_admin_role(client):
    admin = User.query.filter_by(username='admin').first()
    if admin is None:
        admin = User(username='admin', password_hash=generate_password_hash('admin'), role='admin')
        db.session.add(admin)
        db.session.commit()
    client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    with client.session_transaction() as session:
        assert '_user_id' in session  # Check session to verify login
    response = client.get('/users')
    assert response.status_code == 200


def test_redirection(client):
    response = client.get('/users', follow_redirects=True)
    assert response.status_code == 200
    response = client.get('/login', follow_redirects=True)
    assert response.status_code == 200
    response = client.get('/register', follow_redirects=True)
    assert response.status_code == 200
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200