# from fastapi import FastAPI, HTTPException, Body, Depends
# from sqlalchemy.orm import Session
# import logging

# # New imports
# from database.database import engine, Base, get_db
# from crud import operations
# from models import db_models

# from scraper.scraper import ShopifyScraper
# from models.pydantic_models import BrandInsights, ScrapeRequest

# # Create all database tables when the application starts
# # This looks at all the classes inheriting from Base and creates them
# db_models.Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title="Shopify Store Insights Fetcher",
#     description="An API to fetch and structure data from Shopify stores.",
# )

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# @app.post("/fetch-insights/", response_model=BrandInsights)
# async def fetch_store_insights(
#     request: ScrapeRequest,
#     db: Session = Depends(get_db) # <-- FastAPI dependency injection
# ):
#     """
#     Accepts a Shopify store URL, returns structured insights, and saves them to the DB.
#     """
#     logger.info(f"Received request for URL: {request.website_url}")
#     try:
#         scraper = ShopifyScraper(str(request.website_url))
#         insights = scraper.run()
        
#         # --- NEW DATABASE LOGIC ---
#         logger.info(f"Saving insights to the database for {request.website_url}")
#         operations.create_or_update_brand_insights(db=db, insights=insights)
#         logger.info("Successfully saved insights.")
#         # -------------------------
        
#         return insights
        
#     except ValueError as e:
#         logger.error(f"Validation error for {request.website_url}: {e}")
#         raise HTTPException(status_code=404, detail=f"Website not found or failed to process: {e}")
#     except Exception as e:
#         logger.exception(f"An internal error occurred for {request.website_url}")
#         raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Shopify Insights Fetcher API!"}

from fastapi import FastAPI, HTTPException, Body
from scraper.scraper import ShopifyScraper
from models.pydantic_models import BrandInsights, ScrapeRequest
import logging

app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="An API to fetch and structure data from Shopify stores.",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/fetch-insights/", response_model=BrandInsights)
async def fetch_store_insights(request: ScrapeRequest):
    """
    Accepts a Shopify store URL and returns a structured JSON of brand insights.
    """
    logger.info(f"Received request for URL: {request.website_url}")
    try:
        scraper = ShopifyScraper(str(request.website_url))
        insights = scraper.run()
        return insights
    except ValueError as e:
        logger.error(f"Validation error for {request.website_url}: {e}")
        # Using 404 to indicate the resource (website) might not be accessible or valid
        raise HTTPException(status_code=404, detail=f"Website not found or failed to process: {e}")
    except Exception as e:
        logger.exception(f"An internal error occurred for {request.website_url}")
        # Generic catch-all for other unexpected errors
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Shopify Insights Fetcher API!"}