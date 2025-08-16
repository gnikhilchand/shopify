import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from models.pydantic_models import BrandInsights, Product, SocialHandles, ContactDetails, FAQItem
from typing import List, Optional

class ShopifyScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException:
            return None

    def fetch_product_catalog(self) -> List[Product]:
        products_url = f"{self.base_url}/products.json"
        products_list = []
        try:
            response = self.session.get(f"{products_url}?limit=250", timeout=15)
            response.raise_for_status()
            products_data = response.json().get('products', [])
            
            for item in products_data:
                price = float(item.get('variants', [{}])[0].get('price', 0.0))
                product = Product(
                    id=item['id'],
                    title=item['title'],
                    vendor=item['vendor'],
                    product_type=item['product_type'],
                    price=price,
                    url=f"{self.base_url}/products/{item['handle']}"
                )
                products_list.append(product)
        except (requests.RequestException, ValueError):
            pass
        return products_list

    def find_important_links(self, soup: BeautifulSoup) -> dict:
        # CORRECTED: Added "faqs" to the initial dictionary
        links = {"contact_us": None, "privacy_policy": None, "refund_policy": None, "blogs": None, "track_order": None, "faqs": None}
        keywords = {
            "contact": "contact_us",
            "privacy": "privacy_policy",
            "refund": "refund_policy",
            "return": "refund_policy",
            "blog": "blogs",
            "track": "track_order",
            "faq": "faqs",
            "frequently asked questions": "faqs"
        }
        
        for a_tag in soup.find_all('a', href=True):
            link_text = a_tag.get_text(strip=True).lower()
            href = a_tag['href']
            
            for keyword, key in keywords.items():
                if keyword in link_text or keyword in href:
                    if not links[key]:
                        links[key] = urljoin(self.base_url, href)
        return links
    
    def extract_social_handles(self, soup: BeautifulSoup) -> SocialHandles:
        handles = {}
        social_patterns = {
            'instagram': r'instagram\.com/([a-zA-Z0-9_\.]+)',
            'facebook': r'facebook\.com/([a-zA-Z0-9_\.]+)',
            'twitter': r'twitter\.com/([a-zA-Z0-9_]+)',
            'tiktok': r'tiktok\.com/@([a-zA-Z0-9_\.]+)',
            'youtube': r'youtube\.com/(user/|channel/|c/)?([a-zA-Z0-9_\-]+)',
        }
        for a_tag in soup.find_all("a", href=True):
            for platform, pattern in social_patterns.items():
                if platform not in handles and re.search(pattern, a_tag['href']):
                    handles[platform] = a_tag['href']
        return SocialHandles(**handles)

    def extract_contact_details(self, soup: BeautifulSoup) -> ContactDetails:
        text = soup.get_text()
        emails = list(set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)))
        phones = list(set(re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)))
        return ContactDetails(emails=emails, phone_numbers=phones)
    
    def extract_hero_products(self, soup: BeautifulSoup, full_catalog: List[Product]) -> List[Product]:
        hero_products = []
        product_handles = set()
        for a_tag in soup.select('a[href*="/products/"]'):
            href = a_tag.get('href')
            if href and "/products/" in href:
                handle = href.split('/products/')[-1].split('?')[0]
                product_handles.add(handle)

        for product in full_catalog:
            product_url = str(product.url)
            for handle in product_handles:
                if product_url.endswith(handle):
                    hero_products.append(product)
                    break
        return hero_products
    
    def extract_brand_context(self, soup: BeautifulSoup) -> Optional[str]:
        """Extracts brand context from the meta description tag."""
        brand_description = soup.find('meta', attrs={'name': 'description'})
        return brand_description['content'] if brand_description else None

    def extract_faqs(self, faq_page_url: Optional[str]) -> List[FAQItem]:
        if not faq_page_url:
            return []
        faq_soup = self._get_soup(faq_page_url)
        if not faq_soup:
            return []
        faq_list = []
        for item in faq_soup.select('details.accordion__item'):
            question_tag = item.find('summary')
            answer_tag = item.find('div', class_='accordion__content')
            if question_tag and answer_tag:
                question = question_tag.get_text(strip=True)
                answer = answer_tag.get_text(strip=True, separator='\n')
                faq_list.append(FAQItem(question=question, answer=answer))
        return faq_list

    def run(self) -> BrandInsights:
        homepage_soup = self._get_soup(self.base_url)
        if not homepage_soup:
            raise ValueError("Could not fetch the website's homepage.")
            
        links = self.find_important_links(homepage_soup)
        contact_soup = self._get_soup(links.get('contact_us')) if links.get('contact_us') else homepage_soup
        
        contacts_home = self.extract_contact_details(homepage_soup)
        contacts_page = self.extract_contact_details(contact_soup) if contact_soup else ContactDetails()
        
        all_emails = list(set(contacts_home.emails + contacts_page.emails))
        all_phones = list(set(contacts_home.phone_numbers + contacts_page.phone_numbers))

        # CORRECTED: Fetch catalog only once for efficiency
        full_product_catalog = self.fetch_product_catalog()

        insights = BrandInsights(
            store_url=self.base_url,
            product_catalog=full_product_catalog,
            hero_products=self.extract_hero_products(homepage_soup, full_product_catalog),
            brand_context=self.extract_brand_context(homepage_soup),
            social_handles=self.extract_social_handles(homepage_soup),
            contact_details=ContactDetails(emails=all_emails, phone_numbers=all_phones),
            privacy_policy_url=links.get('privacy_policy'),
            refund_policy_url=links.get('refund_policy'),
            faqs=self.extract_faqs(links.get("faqs")),
            important_links=links
        )
        return insights
    

    
# import requests
# import re
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# from models.pydantic_models import BrandInsights, Product, SocialHandles, ContactDetails, FAQItem
# from typing import List, Optional


# class ShopifyScraper:
#     def __init__(self, base_url: str):
#         self.base_url = base_url.rstrip('/')
#         self.session = requests.Session()
#         self.session.headers.update({
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         })

#     def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
#         try:
#             response = self.session.get(url, timeout=10)
#             response.raise_for_status()
#             return BeautifulSoup(response.content, 'html.parser')
#         except requests.RequestException:
#             return None

#     def fetch_product_catalog(self) -> List[Product]:
#         """Fetches all products from the /products.json endpoint."""
#         products_url = f"{self.base_url}/products.json"
#         products_list = []
#         try:
#             response = self.session.get(f"{products_url}?limit=250", timeout=15)
#             response.raise_for_status()
#             products_data = response.json().get('products', [])
            
#             for item in products_data:
#                 # Assuming the first variant has the representative price
#                 price = float(item.get('variants', [{}])[0].get('price', 0.0))
#                 product = Product(
#                     id=item['id'],
#                     title=item['title'],
#                     vendor=item['vendor'],
#                     product_type=item['product_type'],
#                     price=price,
#                     url=f"{self.base_url}/products/{item['handle']}"
#                 )
#                 products_list.append(product)
#         except (requests.RequestException, ValueError):
#             # Fallback or log error if .json endpoint fails
#             pass
#         return products_list

#     def find_important_links(self, soup: BeautifulSoup) -> dict:
#         """Finds key pages like policies, contact, etc."""
#         links = {"contact_us": None, "privacy_policy": None, "refund_policy": None, "blogs": None, "track_order": None}
#         keywords = {
#             "contact": "contact_us",
#             "privacy": "privacy_policy",
#             "refund": "refund_policy",
#             "return": "refund_policy", # Alias for refund
#             "blog": "blogs",
#             "track": "track_order",
#             "faq": "faqs", # Add this line
#             "frequently asked questions": "faqs" # And this for good measure
#         }
        
#         for a_tag in soup.find_all('a', href=True):
#             link_text = a_tag.get_text(strip=True).lower()
#             href = a_tag['href']
            
#             for keyword, key in keywords.items():
#                 if keyword in link_text or keyword in href:
#                     if not links[key]: # Assign only if not already found
#                         links[key] = urljoin(self.base_url, href)
#         return links
    
#     def extract_social_handles(self, soup: BeautifulSoup) -> SocialHandles:
#         """Extracts social media links from the page."""
#         handles = {}
#         social_patterns = {
#             'instagram': r'instagram\.com/([a-zA-Z0-9_\.]+)',
#             'facebook': r'facebook\.com/([a-zA-Z0-9_\.]+)',
#             'twitter': r'twitter\.com/([a-zA-Z0-9_]+)',
#             'tiktok': r'tiktok\.com/@([a-zA-Z0-9_\.]+)',
#             'youtube': r'youtube\.com/(user/|channel/|c/)?([a-zA-Z0-9_\-]+)',
#         }
#         for a_tag in soup.find_all("a", href=True):
#             for platform, pattern in social_patterns.items():
#                 if platform not in handles and re.search(pattern, a_tag['href']):
#                     handles[platform] = a_tag['href']
#         return SocialHandles(**handles)

#     def extract_contact_details(self, soup: BeautifulSoup) -> ContactDetails:
#         """Extracts emails and phone numbers from text."""
#         text = soup.get_text()
#         emails = list(set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)))
#         # Simple regex for phone numbers, can be improved for different formats
#         phones = list(set(re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)))
#         return ContactDetails(emails=emails, phone_numbers=phones)
    
#     def extract_hero_products(self, soup: BeautifulSoup, full_catalog: List[Product]) -> List[Product]:
#         """
#         Finds product links on the homepage and matches them with the full product catalog.
#         """
#         hero_products = []
#         product_handles = set() # Use a set to avoid duplicates

#         # Inspect the homepage HTML (e.g., memy.co.in) to find the right tags and classes.
#         # This selector might need to be adjusted for different sites, but it's a good start.
#         for a_tag in soup.select('a[href*="/products/"]'):
#             href = a_tag.get('href')
#             if href and "/products/" in href:
#                 # Extract the product "handle" from the URL
#                 # e.g., "/products/my-cool-product" -> "my-cool-product"
#                 handle = href.split('/products/')[-1].split('?')[0]
#                 product_handles.add(handle)

#         # Now, find these products in the full catalog you already fetched
#         for product in full_catalog:
#             product_url = str(product.url)
#             for handle in product_handles:
#                 if product_url.endswith(handle):
#                     hero_products.append(product)
#                     break # Move to the next product in the catalog
        
#         return hero_products
    
#     def extract_brand_context(self, soup: BeautifulSoup) -> str:
#         """Extracts brand context or description from the homepage."""
#         # This is a placeholder; actual implementation will depend on the site's structure.
#         # You might look for specific sections or meta tags that describe the brand.
#         brand_description = soup.find('meta', attrs={'name': 'description'})
#         return brand_description['content'] if brand_description else "No brand context found." 
#         # Placeholder for FAQs extraction
#     def extract_faqs(self, faq_page_url: Optional[str]) -> List[FAQItem]:
#         if not faq_page_url:
#             return []

#         faq_soup = self._get_soup(faq_page_url)
#         if not faq_soup:
#             return []

#         faq_list = []
#         # Target each <details> tag which acts as a container for a Q&A pair
#         for item in faq_soup.select('details.accordion__item'):
#             question_tag = item.find('summary')
#             answer_tag = item.find('div', class_='accordion__content')

#             if question_tag and answer_tag:
#                 question = question_tag.get_text(strip=True)
#                 answer = answer_tag.get_text(strip=True, separator='\n')
                
#                 faq_list.append(FAQItem(question=question, answer=answer))
        
#         return faq_list

#     # ... Other methods for hero products, FAQs, brand context ...

#     def run(self) -> BrandInsights:
#         """Orchestrates the scraping process."""
#         homepage_soup = self._get_soup(self.base_url)
#         if not homepage_soup:
#             raise ValueError("Could not fetch the website's homepage.")
            
#         links = self.find_important_links(homepage_soup)
#         contact_soup = self._get_soup(links.get('contact_us')) if links.get('contact_us') else homepage_soup
        
#         # Combine contacts from homepage and contact page
#         contacts_home = self.extract_contact_details(homepage_soup)
#         contacts_page = self.extract_contact_details(contact_soup) if contact_soup else ContactDetails()
        
#         all_emails = list(set(contacts_home.emails + contacts_page.emails))
#         all_phones = list(set(contacts_home.phone_numbers + contacts_page.phone_numbers))

#         insights = BrandInsights(
#             store_url=self.base_url,
#             product_catalog=self.fetch_product_catalog(),
#             social_handles=self.extract_social_handles(homepage_soup),
#             contact_details=ContactDetails(emails=all_emails, phone_numbers=all_phones),
#             privacy_policy_url=links.get('privacy_policy'),
#             refund_policy_url=links.get('refund_policy'),
#             important_links=links,
#             # Assuming you have methods to extract hero products, brand context, and FAQs
#             hero_products=self.extract_hero_products(homepage_soup, self.fetch_product_catalog()),
#             brand_context=self.extract_brand_context(homepage_soup),
#             faqs=self.extract_faqs(links.get("faqs")),
#             # Add other data points as needed
            
#         )
#         return insights