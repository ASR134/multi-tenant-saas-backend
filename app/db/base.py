from sqlalchemy.orm import DeclarativeBase 
# importing sqlalchemy's base class for declarative ORM models

class Base(DeclarativeBase):
    pass
# all sqlalchemy models will inherit from the class Base
# Base.metadata contains the information about the tables represented by models that inherit from Base.

