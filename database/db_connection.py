from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine("mysql+pymysql://root:mysql123@localhost:3306/tnea")
engine = create_engine("mysql+pymysql://tnea_admin:M3ER8MfzddLDjPdf@161.97.142.217:13306/tnea")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class CandidateAllotment(Base):
    __tablename__ = 'candidate_allotment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    s_no = Column(Integer, nullable=True)
    aggr_mark = Column(Float)
    general_rank = Column(String(10))
    community_rank = Column(String(10))
    community = Column(String(50))
    college_code = Column(String(10))
    branch_code = Column(String(10))
    allotted_category = Column(String(50))
    year = Column(Integer)
    round = Column(String(10))


class Branch(Base):
    __tablename__ = 'branch'
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_code = Column(String(10), nullable=True)
    branch_name = Column(String(300), nullable=True)


class Colleges(Base):
    __tablename__ = 'colleges'
    s_no = Column(Integer, nullable=True)
    college_code = Column(Integer, primary_key=True)
    college_name = Column(String(512), nullable=True)
    location = Column(String(512), nullable=True)
    region = Column(String(100), nullable=True)


Base.metadata.create_all(engine)
