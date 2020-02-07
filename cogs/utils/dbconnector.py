from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base


class DatabaseHandler:
    Base = declarative_base()
    session = None

    @classmethod
    def init(cls,url="sqlite:///db1.db"):
        cls.engine = create_engine(url,echo=False)
        cls.newSession()

    @classmethod
    def createTables(cls):
        cls.Base.metadata.create_all(bind=cls.engine)

    @classmethod
    def newSession(cls):
        Session = sessionmaker(bind=cls.engine,expire_on_commit=False)
        cls.session = Session()

    @classmethod
    def commit(cls):
        cls.session.commit()

    @classmethod
    def closeSession(cls):
        cls.session.close()

    @classmethod
    def addItem(cls, item):
        cls.session.add(item)
        cls.session.commit()

    @classmethod
    def getTables(cls):
        print(cls.Base.metadata.tables.keys())
        