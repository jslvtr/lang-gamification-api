from sqlalchemy import and_


class SearchableModel:
    @classmethod
    def search_by_name(cls, search_term, module_id=None):
        if module_id:
            return cls.query.filter(and_(cls.module_id == module_id, cls.name.contains(search_term))).all()
        else:
            return cls.query.filter(cls.name.contains(search_term)).all()
