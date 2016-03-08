from app import db
import models.cities.constants as CityConstants
import common.helper_tables as HelperTables


class City(db.Model):
    __tablename__ = CityConstants.TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    gold = db.Column(db.Integer, unique=False)
    dialog = db.Column(db.Integer, unique=False)
    experience = db.Column(db.Integer, unique=False)
    level = db.Column(db.Integer, unique=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User',
                            backref=db.backref('cities', lazy='dynamic'))
    module = db.relationship('Module', secondary=HelperTables.cities_modules,
                             backref=db.backref('city', uselist=False), uselist=False)

    def __init__(self, name, user_owner, module, gold=100, dialog=0, experience=0, level=1):
        self.name = name
        self.owner = user_owner
        self.module = module
        self.gold = gold
        self.dialog = dialog
        self.experience = experience
        self.level = level

    def next_level_experience(self):
        return self.level * 50 + max(0, (self.level - 199) * 450)

    def experience_required_to_level_up(self):
        return self.next_level_experience() - self.experience

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()
