from scrapy_redis.spiders import RedisSpider
from scrapy import Request
from typing import Generator, Optional, Dict, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class FinanceSpider(RedisSpider):
    """Base spider for scraping financial data."""
    
    name = 'finance'
    redis_key = 'finance:start_urls'
    
    custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': True,
        'ROBOTSTXT_OBEY': True,
    }

    def parse(self, response) -> Generator[Dict[str, Any], None, None]:
        """Parse financial data from listing pages."""
        try:
            # Extract stock/crypto symbols from listing page
            symbols = response.css('.symbol-link::attr(href)').getall()
            
            for symbol_url in symbols:
                yield Request(
                    url=response.urljoin(symbol_url),
                    callback=self.parse_financial_data,
                    errback=self.handle_error,
                    meta={'symbol': symbol_url.split('/')[-1]}
                )

            # Handle pagination
            next_page = response.css('.pagination .next::attr(href)').get()
            if next_page:
                yield Request(
                    url=response.urljoin(next_page),
                    callback=self.parse,
                    errback=self.handle_error
                )
                
        except Exception as e:
            logger.error(f"Error parsing listing page {response.url}: {str(e)}")
            
    def parse_financial_data(self, response) -> Generator[Dict[str, Any], None, None]:
        """Parse detailed financial data for a symbol."""
        try:
            financial_data = {
                'symbol': response.meta.get('symbol'),
                'url': response.url,
                'timestamp': self.get_timestamp(),
                'price': self.extract_text(response, '.current-price'),
                'change': self.extract_text(response, '.price-change'),
                'change_percent': self.extract_text(response, '.price-change-percent'),
                'volume': self.extract_text(response, '.volume'),
                'market_cap': self.extract_text(response, '.market-cap'),
                'pe_ratio': self.extract_text(response, '.pe-ratio'),
                'dividend_yield': self.extract_text(response, '.dividend-yield'),
                '52_week_high': self.extract_text(response, '.52-week-high'),
                '52_week_low': self.extract_text(response, '.52-week-low'),
                'metrics': self.extract_metrics(response),
                'news': self.extract_news(response)
            }
            
            # Extract historical data if available
            historical_data = self.extract_historical_data(response)
            if historical_data:
                financial_data['historical_data'] = historical_data
                
            yield self.clean_financial_data(financial_data)
            
        except Exception as e:
            logger.error(f"Error parsing financial data for {response.url}: {str(e)}")
    
    def extract_text(self, response, selector: str) -> Optional[str]:
        """Safely extract text from a CSS selector."""
        try:
            return response.css(f'{selector}::text').get().strip()
        except:
            return None
            
    def extract_metrics(self, response) -> Dict[str, Any]:
        """Extract financial metrics."""
        metrics = {}
        metric_rows = response.css('.financial-metric')
        
        for row in metric_rows:
            try:
                key = row.css('.metric-name::text').get().strip()
                value = row.css('.metric-value::text').get().strip()
                if key and value:
                    metrics[key] = self.parse_numeric(value)
            except:
                continue
                
        return metrics
        
    def extract_news(self, response) -> list:
        """Extract related news articles."""
        news_items = []
        news_elements = response.css('.news-item')
        
        for element in news_elements:
            try:
                news = {
                    'title': element.css('.news-title::text').get().strip(),
                    'url': element.css('.news-link::attr(href)').get(),
                    'source': element.css('.news-source::text').get().strip(),
                    'timestamp': element.css('.news-timestamp::text').get().strip()
                }
                news_items.append(news)
            except:
                continue
                
        return news_items
        
    def extract_historical_data(self, response) -> Optional[list]:
        """Extract historical price data."""
        try:
            # Often historical data is embedded in a script tag as JSON
            data_script = response.css('script#historical-data::text').get()
            if data_script:
                return json.loads(data_script)
        except:
            return None
            
    def parse_numeric(self, value: str) -> Optional[float]:
        """Convert string numbers to float, handling common financial formats."""
        try:
            # Remove currency symbols and commas
            clean_value = value.replace('$', '').replace(',', '')
            
            # Handle percentages
            if '%' in clean_value:
                return float(clean_value.replace('%', '')) / 100
                
            # Handle billions
            if 'B' in clean_value:
                return float(clean_value.replace('B', '')) * 1_000_000_000
                
            # Handle millions
            if 'M' in clean_value:
                return float(clean_value.replace('M', '')) * 1_000_000
                
            return float(clean_value)
        except:
            return None
        
    def clean_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate financial data."""
        return {k: v for k, v in data.items() if v is not None}
        
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat()
        
    def handle_error(self, failure):
        """Handle request failures."""
        logger.error(f"Request failed: {failure.request.url}")
        logger.error(f"Error: {str(failure.value)}")
