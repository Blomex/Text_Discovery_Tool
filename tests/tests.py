from unittest.mock import patch

from flask_testing import TestCase

from main import load_user, index, app


# User.get = MagicMock(return_value=mocked_user)
# current_user = MagicMock()
# current_user.is_authorized(return_value=True)

def test_load_user():
    mocked_user = {
        "access_token": "123",
        "expires_in": "3599",
        "scope": "openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
        "token_type": "Bearer",
        "id_token": "123"
    }
    with patch('models.User.User.get') as get_mock:
        get_mock.return_value = mocked_user
        assert load_user(1) == mocked_user


class MyTest(TestCase):
    render_templates = False

    def create_app(self):
        return app

    def test_logged_user(self):
        with patch('flask_login.utils._get_user') as user_mock:
            user_mock.return_value.is_authenticated = True
            index()
            self.assert_template_used('index.html')

    def test_not_logged_user(self):
        with patch('flask_login.utils._get_user') as user_mock:
            user_mock.return_value.is_authenticated = False
            index()
            self.assert_template_used('not_logged.html')
