import uuid
from common.database import Database
import models.modules.constants as ModuleConstants
from models.modules.errors import NotOwnerException

__author__ = 'jslvtr'


class Module(object):
    def __init__(self, name, owner, id_=None):
        self.name = name
        self.owner = owner
        self.editors = list()
        self._id = uuid.uuid4().hex if id_ is None else id_

    def __repr__(self):
        return "<Module {}, {}>".format(self.name, self._id)

    @classmethod
    def find_by_id(cls, id_):
        return cls(**Database.find_one(ModuleConstants.COLLECTION, {"_id": id_}))

    @staticmethod
    def allowed(module_id, user_email):
        module = Module.find_by_id(module_id)

        return module.check_access_allowed(user_email)

    @staticmethod
    def delete(module_id, user):
        module = Module.find_by_id(module_id)

        if user.get_id() == module.owner:
            return True
        else:
            raise NotOwnerException("You are not the owner of this project, so you cannot delete it.")

    def check_access_allowed(self, user_email):
        return user_email in self.editors

    def add_editor(self, editor):
        self.editors.append(editor)
        self.save_to_db()

    def save_to_db(self):
        Database.insert(ModuleConstants.COLLECTION, self.json())

    def json(self):
        return {
            "name": self.name,
            "editors": self.editors,
            "owner": self.owner,
            "_id": self._id
        }
