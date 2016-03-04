from sqlalchemy import and_


class SearchableModel:
    @classmethod
    def search_by_name(cls, search_term, module_id=None, order_by=None, direction=1):
        if module_id:
            result = cls.query.filter(and_(cls.module_id == module_id, cls.name.contains(search_term))).order_by(cls.order.asc())
        else:
            result = cls.query.filter(cls.name.contains(search_term))
        cls.sort_filter(result, order_by, direction)
        return result

    @classmethod
    def sort_filter(cls, data, order_by, direction):
        if not order_by:
            return data.all()
        if direction > 0:
            return data.order_by(order_by.asc()).all()
        else:
            return data.order_by(order_by.desc()).all()