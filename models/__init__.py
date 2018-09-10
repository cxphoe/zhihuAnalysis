from db import SQLDB

class Model():
    session = SQLDB.session
    '''
    用来显示爬虫信息 model
    '''
    
    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n {}>'.format(name, '\n '.join(properties))
        return s

    @classmethod
    def columns(cls):
        return cls.__mapper__.c.keys()

    @classmethod
    def all(cls, fields=None):
        if fields is None:
            result = cls.session.query(cls)
        else:
            result = cls.session.query(*[getattr(cls, f) for f in fields])
        
        return result

    def save(self):
        self.session.add(self)
        self.session.commit()

