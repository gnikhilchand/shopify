/shopify-insights-app
├── main.py                 # FastAPI application entry point and API routes
├── scraper/
│   ├── scraper.py          # Core Scraper class with logic to fetch and parse data
│   └── utils.py            # Helper functions (e.g., making HTTP requests)
├── models/
│   ├── pydantic_models.py  # Pydantic models for API request/response
│   └── db_models.py        # (Bonus) SQLAlchemy models for the database
├── crud/
│   └── operations.py       # (Bonus) Functions for database interactions
├── database/
│   └── database.py         # (Bonus) Database session setup
├── requirements.txt        # Project dependencies
└── .env                    # Environment variables (e.g., DB connection string)
