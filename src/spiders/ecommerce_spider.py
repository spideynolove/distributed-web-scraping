from scrapy_redis.spiders import RedisSpider
from scrapy import Request
from typing import Generator, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EcommerceSpider(RedisSpider):
    """Base spider for scraping e-commerce websites."""
    
    name = 'ecommerce'
    redis_key = 'ecommerce:start_urls'
    
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 1,
        'COOKIES_ENABLED': False,
    }

    def parse(self, response) -> Generator[Dict[str, Any], None, None]:
        """Parse product listing pages and follow links to product details."""
        try:
            # Extract product links from listing page
            product_links = response.css('a.product-link::attr(href)').getall()
            
            for link in product_links:
                yield Request(
                    url=response.urljoin(link),
                    callback=self.parse_product,
                    errback=self.handle_error,
                    dont_filter=False
                )

            # Follow pagination
            next_page = response.css('a.next-page::attr(href)').get()
            if next_page:
                yield Request(
                    url=response.urljoin(next_page),
                    callback=self.parse,
                    errback=self.handle_error
                )
                
        except Exception as e:
            logger.error(f"Error parsing listing page {response.url}: {str(e)}")
            
    def parse_product(self, response) -> Generator[Dict[str, Any], None, None]:
        """Parse individual product pages."""
        try:
            product_data = {
                'url': response.url,
                'name': self.extract_text(response, '.product-name'),
                'price': self.extract_text(response, '.product-price'),
                'currency': self.extract_text(response, '.currency'),
                'description': self.extract_text(response, '.product-description'),
                'sku': self.extract_text(response, '.product-sku'),
                'brand': self.extract_text(response, '.product-brand'),
                'category': self.extract_text(response, '.product-category'),
                'availability': self.extract_text(response, '.product-availability'),
                'rating': self.extract_text(response, '.product-rating'),
                'review_count': self.extract_text(response, '.review-count'),
                'images': response.css('img.product-image::attr(src)').getall(),
                'specifications': self.extract_specifications(response),
                'variants': self.extract_variants(response),
                'timestamp': self.get_timestamp()
            }
            
            yield self.clean_product_data(product_data)
            
        except Exception as e:
            logger.error(f"Error parsing product page {response.url}: {str(e)}")
    
    def extract_text(self, response, selector: str) -> Optional[str]:
        """Safely extract text from a CSS selector."""
        try:
            return response.css(f'{selector}::text').get().strip()
        except:
            return None
            
    def extract_specifications(self, response) -> Dict[str, str]:
        """Extract product specifications."""
        specs = {}
        spec_rows = response.css('.specification-row')
        
        for row in spec_rows:
            try:
                key = row.css('.spec-key::text').get().strip()
                value = row.css('.spec-value::text').get().strip()
                if key and value:
                    specs[key] = value
            except:
                continue
                
        return specs
        
    def extract_variants(self, response) -> list:
        """Extract product variants."""
        variants = []
        variant_elements = response.css('.product-variant')
        
        for element in variant_elements:
            try:
                variant = {
                    'name': element.css('.variant-name::text').get().strip(),
                    'price': element.css('.variant-price::text').get().strip(),
                    'sku': element.css('.variant-sku::text').get().strip(),
                }
                variants.append(variant)
            except:
                continue
                
        return variants
        
    def clean_product_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate product data."""
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
        
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
        
    def handle_error(self, failure):
        """Handle request failures."""
        logger.error(f"Request failed: {failure.request.url}")
        logger.error(f"Error: {str(failure.value)}")
