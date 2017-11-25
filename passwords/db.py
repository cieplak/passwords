from sqlalchemy import MetaData as _MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, Table, Unicode, create_engine


def init(absolute_filesystem_path):
    uri = 'sqlite:///{}'.format(absolute_filesystem_path)
    global engine, Session
    engine = create_engine(uri)
    Metadata.bind = engine
    Session = scoped_session(sessionmaker(bind=engine))
    Model.query = Session.query_property()
    Model.Session = Session


engine = None
Session = None
Metadata = _MetaData()


class ModelMixin(object):
    def __repr__(self):
        name = self.__class__.__name__
        values = ', '.join(
            '{}={}'.format(
                key, str(getattr(self, key))
            )
            for key in self.__table__.columns.keys()
        )
        repr = '{}({})'.format(name, values)
        return repr


Model = declarative_base(cls=ModelMixin)


class PasswordModel(Model):

    __table__ = Table(
        'registry', Metadata,
        Column('path',  Unicode, primary_key=True),
        Column('value', Unicode))

    @classmethod
    def save(cls, path, ciphertext):
        record = cls(path=path, value=ciphertext)
        cls.Session.add(record)
        cls.Session.commit()
        return record

    def delete(self):
        self.Session.delete(self)
        self.Session.commit()
