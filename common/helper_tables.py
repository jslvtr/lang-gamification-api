from app import db

students = db.Table('studying',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('module_id', db.Integer, db.ForeignKey('module.id'))
                    )

cities_modules = db.Table('cities_modules',
                          db.Column('city_id', db.Integer, db.ForeignKey('city.id')),
                          db.Column('module_id', db.Integer, db.ForeignKey('module.id'))
                          )

words_tags = db.Table('words_tags',
                      db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                      db.Column('word_id', db.Integer, db.ForeignKey('word.id'))
                      )

completed_lectures = db.Table('completed_lectures',
                              db.Column('lecture_id', db.Integer, db.ForeignKey('lecture.id')),
                              db.Column('city_id', db.Integer, db.ForeignKey('city.id'))
                              )
