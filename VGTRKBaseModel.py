from sqlalchemy import Column, Integer, String, DateTime,  ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///service/database.sqllite3.db', echo=False)
Base = declarative_base()


class Sys_LastUpdate(Base):

    __tablename__ = 'Sys_LastUpdate'
    key = Column(Integer, primary_key=True)
    datetime_lastUpdate = Column(DateTime)

    def __str__(self):
        return f'{self.key}) {self.datetime_lastUpdate }'


class Company(Base):

    __tablename__ = 'Companies'
    company_id = Column(Integer, primary_key=True)
    company_name = Column(String(255))

    procurements = relationship('Procurement')

    def __init__(self, name):
        self.company_name = name

    def __str__(self):
        return f'{self.company_id}) {self.company_name}'


class State(Base):

    __tablename__ = 'States'
    state_id = Column(Integer, primary_key=True)
    state_name = Column(String(255))

    def __init__(self, name):
        self.state_name = name

    def __str__(self):
        return f'{self.state_id}) {self.state_name}'


class Procurement(Base):

    __tablename__ = 'Procurements'
    procurement_id = Column(Integer, primary_key=True)
    procurement_num = Column(String(20))
    procurement_company_id = Column(Integer, ForeignKey('Companies.company_id'))
    procurement_description = Column(String(2048))
    procurement_price = Column(Integer)
    procurement_start = Column(DateTime)
    procurement_finish = Column(DateTime)
    procurement_state_id = Column(Integer, ForeignKey('States.state_id'))
    procurement_href = Column(String(512))

    def __str__(self):
        return f'{self.procurement_id}) {self.procurement_num}'


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
