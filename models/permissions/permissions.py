from common.database import Database
from models.permissions.errors import PermissionsCreationError
import models.permissions.constants as PermissionConstants

__author__ = 'jslvtr'


class Permissions(object):

    def __init__(self, name, access, default=0):
        self.name = name
        Permissions._check_access_list(access)
        self.access = access
        self.default = default

    @staticmethod
    def _check_access_list(access):
        if not isinstance(access, list):
            raise PermissionsCreationError("The access parameter must be a list")
        for level in access:
            if level not in PermissionConstants.TYPES:
                raise PermissionsCreationError(
                    "The access parameter had an access type that is not allowed (only use {})".format(
                        PermissionConstants.TYPES))

    @classmethod
    def default(cls):
        data = Database.find_one(collection=PermissionConstants.COLLECTION,
                                 query={'default': 1})
        del data['_id']
        return cls(**data)

    @classmethod
    def find_by_name(cls, name):
        data = Database.find_one(collection=PermissionConstants.COLLECTION,
                                 query={'name': name})
        del data['_id']
        return cls(**data)

    @classmethod
    def access_to(cls, type_):
        """
        Returns what access levels are allowed to visit a specific type of page or artifact

        When accessing the admin page, call user.permissions.allowed(Permissions.access_to('admin'))
        :param type_:
        :return:
        """

        if type_ not in PermissionConstants.TYPES:
            raise PermissionsCreationError(
                "The type parameter had an access type that is not allowed (only use {})".format(PermissionConstants.TYPES))
        access_levels = Database.find(PermissionConstants.COLLECTION, {"access": {'$in': [type_]}})
        return [level['name'] for level in access_levels]

    @classmethod
    def set_default(cls, name):
        try:
            current_default = cls.default()
            new_default = cls.find_by_name(name)

            current_default.default = 0
            current_default.save_to_db()

            new_default.default = 1
            new_default.save_to_db()
            return True
        except:
            return False

    def allowed(self, access_levels):
        return self.name in [level for level in access_levels]

    def save_to_db(self):
        Database.update(PermissionConstants.COLLECTION, {"name": self.name}, {'$set': self.json()}, upsert=True)

    @staticmethod
    def remove_from_db(name):
        Database.remove(PermissionConstants.COLLECTION, {'name': name})

    def json(self):
        json = {
            "name": self.name,
            "access": self.access,
            "default": self.default
        }

        return json
