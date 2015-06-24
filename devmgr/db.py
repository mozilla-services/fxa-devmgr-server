import uuid

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection


def new_uuid():
    return str(uuid.uuid4())


Base = declarative_base()


class Device(Base):
    __tablename__ = 'devices'

    uuid = Column(String, primary_key=True, default=new_uuid)
    account_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    endpoint = Column(String)
    tokens = relationship(
        "Token", collection_class=attribute_mapped_collection('token_hash'),
        cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def to_json(self):
        return dict(uuid=self.uuid, name=self.name, endpoint=self.endpoint)


class Token(Base):
    __tablename__ = 'tokens'

    token_hash = Column(String, primary_key=True)
    device_uuid = Column(Integer, ForeignKey('devices.uuid'))

    def __init__(self, token_hash):
        self.token_hash = token_hash
