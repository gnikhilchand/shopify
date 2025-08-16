# from sqlalchemy.orm import Session
# from models import db_models, pydantic_models

# def create_or_update_brand_insights(db: Session, insights: pydantic_models.BrandInsights):
#     # 1. Check if the brand already exists in our database
#     db_brand = db.query(db_models.Brand).filter(db_models.Brand.store_url == str(insights.store_url)).first()

#     if db_brand:
#         # If it exists, update its fields
#         print(f"Updating existing brand: {insights.store_url}")
#         db_brand.brand_context = insights.brand_context
#         db_brand.social_handles = insights.social_handles.model_dump()
#         db_brand.contact_details = insights.contact_details.model_dump()
        
#         # Simple strategy: delete old products and add the new list
#         db.query(db_models.Product).filter(db_models.Product.brand_id == db_brand.id).delete()
#     else:
#         # If it doesn't exist, create a new Brand object
#         print(f"Creating new brand: {insights.store_url}")
#         db_brand = db_models.Brand(
#             store_url=str(insights.store_url),
#             brand_context=insights.brand_context,
#             social_handles=insights.social_handles.model_dump(),
#             contact_details=insights.contact_details.model_dump()
#         )
#         db.add(db_brand)
#         # We need to flush to get the db_brand.id for the products
#         db.flush()

#     # 2. Add all the products from the scrape to this brand
#     for product in insights.product_catalog:
#         db_product = db_models.Product(
#             shopify_product_id=product.id,
#             title=product.title,
#             vendor=product.vendor,
#             product_type=product.product_type,
#             price=product.price,
#             brand_id=db_brand.id # Link the product to the brand
#         )
#         db.add(db_product)

#     # 3. Commit the transaction to save all changes
#     db.commit()
#     db.refresh(db_brand)
#     return db_brand

from sqlalchemy.orm import Session
from models import db_models, pydantic_models

def create_brand_insights(db: Session, insights: pydantic_models.BrandInsights):
    # Check if brand already exists
    db_brand = db.query(db_models.Brand).filter(db_models.Brand.store_url == str(insights.store_url)).first()
    if not db_brand:
        db_brand = db_models.Brand(store_url=str(insights.store_url), brand_context=insights.brand_context)
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)
    
    # Simple example for products
    for product in insights.product_catalog:
        db_product = db.query(db_models.Product).filter(db_models.Product.shopify_product_id == product.id).first()
        if not db_product:
            new_prod = db_models.Product(
                shopify_product_id=product.id,
                title=product.title,
                vendor=product.vendor,
                price=product.price,
                brand_id=db_brand.id
            )
            db.add(new_prod)
    db.commit()
    return db_brand