from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class Product(BaseModel):
    id: int
    title: str
    vendor: str
    product_type: str
    price: float
    url: HttpUrl

class FAQItem(BaseModel):
    question: str
    answer: str

class SocialHandles(BaseModel):
    instagram: Optional[HttpUrl] = None
    facebook: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    tiktok: Optional[HttpUrl] = None
    youtube: Optional[HttpUrl] = None

class ContactDetails(BaseModel):
    emails: List[str] = []
    phone_numbers: List[str] = []

class BrandInsights(BaseModel):
    store_url: HttpUrl
    brand_context: Optional[str] = Field(None, description="About Us section content.")
    product_catalog: List[Product] = []
    hero_products: List[Product] = []
    social_handles: SocialHandles
    contact_details: ContactDetails
    privacy_policy_url: Optional[HttpUrl] = None
    refund_policy_url: Optional[HttpUrl] = None
    faqs: List[FAQItem] = []
    important_links: dict[str, Optional[HttpUrl]] = {}

class ScrapeRequest(BaseModel):
    website_url: HttpUrl