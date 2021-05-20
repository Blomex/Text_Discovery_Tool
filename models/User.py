from flask_login import UserMixin
from datastore_entity import DatastoreEntity, EntityValue
import datetime
class User(DatastoreEntity, UserMixin):
    id = EntityValue(None)
    username = EntityValue(None)
    password = EntityValue(None)
    status = EntityValue(1)
    @staticmethod
    def get(user_id):
        return users.get(user_id)

    @staticmethod
    def create(user_id, user):
        users[user_id] = user