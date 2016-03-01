from app import db

students = db.Table('studying',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('module_id', db.Integer, db.ForeignKey('module.id'))
                    )