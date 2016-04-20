from app import db

students = db.Table('studying',
                    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                    db.Column('module_id', db.Integer, db.ForeignKey('module.id'))
                    )

friends = db.Table('friends',
                   db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                   db.Column('friend_id', db.Integer, db.ForeignKey('student.id'))
                   )

active_to_modules = db.Table('cities_modules',
                             db.Column('active_module_id', db.Integer, db.ForeignKey('active_module.id')),
                             db.Column('module_id', db.Integer, db.ForeignKey('module.id'))
                             )

words_tags = db.Table('words_tags',
                      db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                      db.Column('word_id', db.Integer, db.ForeignKey('word.id'))
                      )

lectures_tags = db.Table('lectures_tags',
                         db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                         db.Column('lecture_id', db.Integer, db.ForeignKey('lecture.id'))
                         )

completed_lectures = db.Table('completed_lectures',
                              db.Column('lecture_id', db.Integer, db.ForeignKey('lecture.id')),
                              db.Column('active_module_id', db.Integer, db.ForeignKey('active_module.id'))
                              )

attempt_questions = db.Table('attempt_questions',
                             db.Column('quiz_attempt_id', db.Integer, db.ForeignKey('quiz_attempt.id')),
                             db.Column('question_id', db.Integer, db.ForeignKey('question.id'))
                             )

challenges_questions = db.Table('challenges_questions',
                             db.Column('challenge_id', db.Integer, db.ForeignKey('challenge.id')),
                             db.Column('question_id', db.Integer, db.ForeignKey('question.id'))
                             )