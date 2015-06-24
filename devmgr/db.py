import uuid

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base


def new_uuid():
    return str(uuid.uuid4())


Base = declarative_base()


class Device(Base):
    __tablename__ = 'devices'

    uuid = Column(String, primary_key=True, default=new_uuid)
    account_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    endpoint = Column(String)

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def to_json(self):
        return dict(uuid=self.uuid, name=self.name, endpoint=self.endpoint)
