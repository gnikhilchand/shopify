Shopify Store Insights Fetcher 🛍️
A powerful backend application built with Python and FastAPI to scrape and structure key data from any Shopify store. Provide a store's URL and receive a comprehensive JSON object with its product catalog, policies, social handles, and more.

🌟 Overview
This project provides a robust RESTful API that acts as a specialized web scraper for Shopify-based e-commerce websites. It intelligently navigates a target store to extract valuable business insights without relying on the official Shopify API. The scraped data is then organized into a clean, predictable JSON response and persisted in a MySQL database for future analysis.

The primary goal is to offer a scalable and maintainable system for gathering competitive intelligence and brand data from the Shopify ecosystem.

✨ Features
Complete Product Catalog: Fetches the entire list of products using the /products.json endpoint.

Hero Product Identification: Scrapes the homepage to identify featured products.

Policy Extraction: Automatically finds and provides direct links to Privacy, Refund, and Return policies.

FAQ Scraper: Navigates to the FAQ page and parses all question-and-answer pairs.

Contact & Social Media: Extracts all available contact details (emails, phone numbers) and social media handles (Instagram, Facebook, etc.).

Brand Context: Pulls the brand's "About Us" or meta description text.

Important Links: Identifies key navigation links like "Contact Us," "Track Order," and "Blogs."

Database Persistence (Bonus): Saves all scraped data to a MySQL database using SQLAlchemy for robust storage and retrieval.

Interactive API Docs: Automatically generated, user-friendly API documentation via Swagger UI.

🛠️ Tech Stack
Backend: Python

API Framework: FastAPI

Web Scraping: requests, BeautifulSoup4

Database ORM: SQLAlchemy

Database: MySQL

Data Validation: Pydantic

Server: Uvicorn

🚀 Getting Started
Follow these instructions to get a local copy up and running for development and testing.

Prerequisites
Python 3.10 or higher

A running MySQL server instance

1. Clone the Repository
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name

2. Set Up a Virtual Environment
It's highly recommended to use a virtual environment.

# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment Variables
Create a file named .env in the root directory of the project. This file will hold your database connection string.

# .env file
DATABASE_URL="mysql+pymysql://<user>:<password>@<host>/<dbname>"

Example:
DATABASE_URL="mysql+pymysql://root:mysecretpassword@127.0.0.1/shopify_insights"

5. Set Up the Database
Connect to your MySQL server and create the database you specified in the .env file.

CREATE DATABASE IF NOT EXISTS shopify_insights;

The application will automatically create the necessary tables (brands, products) the first time it starts.

▶️ Running the Application
Once the setup is complete, you can start the API server using Uvicorn.

uvicorn main:app --reload

The server will be running on http://127.0.0.1:8000. The --reload flag enables hot-reloading for development.

kullanım API Usage
You can interact with the API through the automatically generated documentation or by using a tool like curl or Postman.

Interactive Documentation
Navigate to http://127.0.0.1:8000/docs in your browser to access the Swagger UI. Here you can test the endpoint directly.

API Endpoint: POST /fetch-insights/
This is the main endpoint for fetching store data.

Request Body:

{
  "website_url": "https://www.memy.co.in"
}

Success Response (200 OK): A JSON object containing the BrandInsights model.

Error Responses:

404 Not Found: If the website URL is invalid or the server cannot be reached.

500 Internal Server Error: If an unexpected error occurs during the scraping process.

Example curl Request
curl -X POST "http://127.0.0.1:8000/fetch-insights/" \
-H "Content-Type: application/json" \
-d '{
  "website_url": "https://hairoriginals.com/"
}'

📂 Project Structure
The project is organized into modules to ensure a clean and maintainable codebase.

/shopify-insights-app
├── crud/
│   └── operations.py       # Database create/update functions
├── database/
│   └── database.py         # Database engine and session setup
├── models/
│   ├── db_models.py        # SQLAlchemy ORM models (tables)
│   └── pydantic_models.py  # Pydantic models for API data validation
├── scraper/
│   └── scraper.py          # Core web scraping logic
├── .env                    # (Locally created) Environment variables
├── .gitignore              # Files and folders to ignore
├── main.py                 # FastAPI application entry point and routes
└── requirements.txt        # Project dependencies
