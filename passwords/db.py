from sqlalchemy import MetaData as _MetaData, TypeDecorator, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy import Column, Table, Unicode, func


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
