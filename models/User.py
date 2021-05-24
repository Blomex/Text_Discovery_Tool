from flask_login import UserMixin
users = {}
import datetime
class User(UserMixin):
    def __init__(self, id_, email):
        self.id = id_
        self.email = email
    @staticmethod
    def get(user_id):
        return users.get(user_id)
    @staticmethod
    def create(user_id, user):
        users[user_id] = user