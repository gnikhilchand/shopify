# from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
# from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.mysql import JSON
# from database.database import Base

# class Brand(Base):
#     __tablename__ = "brands"

#     id = Column(Integer, primary_key=True, index=True)
#     store_url = Column(String(255), unique=True, index=True, nullable=False)
#     brand_context = Column(Text, nullable=True)

#     # These fields will store structured data as JSON strings
#     social_handles = Column(JSON, nullable=True)
#     contact_details = Column(JSON, nullable=True)
    
#     # This establishes the one-to-many relationship
#     products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")

# class Product(Base):
#     __tablename__ = "products"

#     id = Column(Integer, primary_key=True, index=True)
#     # The original product ID from the Shopify store
#     shopify_product_id = Column(Integer, unique=True, index=True)
#     title = Column(String(255), nullable=False)
#     vendor = Column(String(255))
#     product_type = Column(String(100))
#     price = Column(Float)

#     # This is the foreign key linking back to the Brand table
#     brand_id = Column(Integer, ForeignKey("brands.id"))
#     brand = relationship("Brand", back_populates="products")

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    store_url = Column(String(255), unique=True, index=True)
    brand_context = Column(String(2000))
    products = relationship("Product", back_populates="brand")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    shopify_product_id = Column(Integer, unique=True)
    title = Column(String(255))
    vendor = Column(String(255))
    price = Column(Float)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    brand = relationship("Brand", back_populates="products")

#... other tables for FAQs, Contacts, etc. ...