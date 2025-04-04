# db_control/mymodels.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db_control.connect_MySQL import Base
from datetime import datetime

class Bedandy(Base):
    __tablename__ = "bedandy"

    bedandy_id = Column(Integer, primary_key=True, autoincrement=True)
    family_id = Column(String(50), nullable=False)
    before_photourl = Column(Text, nullable=True)
    after_photourl = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    items = relationship("BdItem", back_populates="bedandy")


class Item(Base):
    __tablename__ = "item"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(255))
    price = Column(String(50))
    brand = Column(String(255))
    description = Column(Text)

    beds = relationship("BdItem", back_populates="item")


class BdItem(Base):
    __tablename__ = "bd_item"

    bi_id = Column(Integer, primary_key=True, autoincrement=True)
    bedandy_id = Column(Integer, ForeignKey("bedandy.bedandy_id"))
    item_id = Column(Integer, ForeignKey("item.item_id"))

    bedandy = relationship("Bedandy", back_populates="items")
    item = relationship("Item", back_populates="beds")

