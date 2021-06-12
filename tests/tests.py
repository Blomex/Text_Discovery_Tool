from unittest.mock import patch

from flask_testing import TestCase
from scale_down.main import resize_image
from main import load_user, index, app
from PIL import Image
from random import randint

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


class LoginTest(TestCase):
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


def test_resize_image():
    for i in range(10):
        random_width = randint(0, 5000)
        random_height = randint(0, 3000)
        image = Image.new('RGBA', size=(random_width, random_height), color = (256, 0, 0))
        result_image = resize_image(image)
        width, height = result_image.size
        if random_width > 1024 or random_height > 768:
            assert height <= 768 and width <= 1024
        else:
            assert width == int(0.9*random_width) and height == int (0.9*random_height)
