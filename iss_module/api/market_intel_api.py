"""
DALS Market Intelligence API
Real-time market data integration for stocks, crypto, and financial news
DALS-001 compliant: Returns real data only, zeros for unavailable data
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
import logging
import json
import time
from datetime import datetime, timezone

# Market data dependencies
try:
    import yfinance as yf
    import feedparser
    import requests
    from pycoingecko import CoinGeckoAPI
    MARKET_DATA_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Market data dependencies not available: {e}")
    MARKET_DATA_AVAILABLE = False
    yf = None
    feedparser = None
    requests = None
    CoinGeckoAPI = None

# Configure logging
logger = logging.getLogger(__name__)

# Market Intelligence API router
market_router = APIRouter(prefix="/markets", tags=["Market Intelligence"])

# Data Models
class MarketIndexes(BaseModel):
    dow: float = Field(default=0.0, description="Dow Jones Industrial Average")
    nasdaq: float = Field(default=0.0, description="NASDAQ Composite")
    sp500: float = Field(default=0.0, description="S&P 500")
    btc: float = Field(default=0.0, description="Bitcoin price (USD)")
    eth: float = Field(default=0.0, description="Ethereum price (USD)")

class StockData(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    changePercent: str = Field(default="0.00%", description="Price change percentage")

class CryptoData(BaseModel):
    symbol: str = Field(..., description="Crypto symbol")
    current_price: float = Field(default=0.0, description="Current price in USD")

class NewsHeadline(BaseModel):
    title: str = Field(..., description="News headline")
    source: str = Field(default="", description="News source")
    timestamp: Optional[str] = Field(None, description="Publication timestamp")

class MarketStatusResponse(BaseModel):
    indexes: MarketIndexes = Field(default_factory=MarketIndexes, description="Market indexes")
    stocks: List[StockData] = Field(default_factory=list, description="Top stocks data")
    crypto: List[CryptoData] = Field(default_factory=list, description="Cryptocurrency data")
    news: List[NewsHeadline] = Field(default_factory=list, description="Financial news headlines")
    last_updated: Optional[str] = Field(None, description="Last data update timestamp")

# Market Data Service
class MarketDataService:
    def __init__(self):
        self.cg = CoinGeckoAPI() if MARKET_DATA_AVAILABLE else None
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        return (time.time() - self.cache[key]['timestamp']) < self.cache_timeout

    def _get_cached_data(self, key: str) -> Any:
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            return self.cache[key]['data']
        return None

    def _set_cached_data(self, key: str, data: Any):
        """Store data in cache"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

    async def get_market_indexes(self) -> MarketIndexes:
        """Get major market indexes - DALS-001 compliant"""
        if not MARKET_DATA_AVAILABLE:
            logger.warning("Market data dependencies not available")
            return MarketIndexes()

        try:
            # Get stock market indexes
            dow_data = yf.Ticker("^DJI").history(period="1d")
            nasdaq_data = yf.Ticker("^IXIC").history(period="1d")
            sp500_data = yf.Ticker("^GSPC").history(period="1d")

            dow = float(dow_data['Close'].iloc[-1]) if not dow_data.empty else 0.0
            nasdaq = float(nasdaq_data['Close'].iloc[-1]) if not nasdaq_data.empty else 0.0
            sp500 = float(sp500_data['Close'].iloc[-1]) if not sp500_data.empty else 0.0

            # Get crypto prices
            btc_price = 0.0
            eth_price = 0.0

            if self.cg:
                try:
                    crypto_data = self.cg.get_price(ids=['bitcoin', 'ethereum'], vs_currencies='usd')
                    btc_price = crypto_data.get('bitcoin', {}).get('usd', 0.0)
                    eth_price = crypto_data.get('ethereum', {}).get('usd', 0.0)
                except Exception as e:
                    logger.warning(f"Failed to fetch crypto prices: {e}")

            return MarketIndexes(
                dow=dow,
                nasdaq=nasdaq,
                sp500=sp500,
                btc=btc_price,
                eth=eth_price
            )

        except Exception as e:
            logger.error(f"Failed to fetch market indexes: {e}")
            return MarketIndexes()

    async def get_top_stocks(self) -> List[StockData]:
        """Get top 20 stocks data - DALS-001 compliant"""
        if not MARKET_DATA_AVAILABLE:
            return []

        cache_key = "top_stocks"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # Top stocks by market cap (sample list)
            top_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
                'BABA', 'ORCL', 'CRM', 'AMD', 'INTC', 'UBER', 'SPOT', 'PYPL',
                'SQ', 'SHOP', 'ZM', 'DOCU'
            ]

            stocks_data = []

            for symbol in top_symbols[:20]:  # Limit to 20
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")

                    if len(hist) >= 2:
                        prev_close = hist['Close'].iloc[-2]
                        current_close = hist['Close'].iloc[-1]
                        change_percent = ((current_close - prev_close) / prev_close) * 100

                        stocks_data.append(StockData(
                            symbol=symbol,
                            changePercent=f"{change_percent:+.2f}%"
                        ))
                    else:
                        stocks_data.append(StockData(
                            symbol=symbol,
                            changePercent="0.00%"
                        ))

                except Exception as e:
                    logger.warning(f"Failed to fetch data for {symbol}: {e}")
                    stocks_data.append(StockData(
                        symbol=symbol,
                        changePercent="0.00%"
                    ))

            self._set_cached_data(cache_key, stocks_data)
            return stocks_data

        except Exception as e:
            logger.error(f"Failed to fetch top stocks: {e}")
            return []

    async def get_crypto_data(self) -> List[CryptoData]:
        """Get cryptocurrency data - DALS-001 compliant"""
        if not MARKET_DATA_AVAILABLE or not self.cg:
            return []

        cache_key = "crypto_data"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            crypto_ids = ['bitcoin', 'ethereum', 'solana', 'dogecoin', 'matic-network']
            crypto_data = self.cg.get_price(ids=crypto_ids, vs_currencies='usd')

            result = []
            for crypto_id in crypto_ids:
                price = crypto_data.get(crypto_id, {}).get('usd', 0.0)
                symbol = crypto_id.split('-')[0] if '-' in crypto_id else crypto_id
                result.append(CryptoData(
                    symbol=symbol.upper(),
                    current_price=price
                ))

            self._set_cached_data(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"Failed to fetch crypto data: {e}")
            return []

    async def get_news_headlines(self) -> List[NewsHeadline]:
        """Get financial news headlines - DALS-001 compliant"""
        if not MARKET_DATA_AVAILABLE:
            return []

        cache_key = "news_headlines"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            headlines = []

            # CNBC RSS Feed
            try:
                cnbc_feed = feedparser.parse('https://www.cnbc.com/id/100003114/device/rss/rss.html')
                for entry in cnbc_feed.entries[:5]:  # Top 5 headlines
                    headlines.append(NewsHeadline(
                        title=entry.title,
                        source="CNBC",
                        timestamp=getattr(entry, 'published', None)
                    ))
            except Exception as e:
                logger.warning(f"Failed to fetch CNBC news: {e}")

            # Bloomberg RSS Feed
            try:
                bloomberg_feed = feedparser.parse('https://feeds.bloomberg.com/markets/news.rss')
                for entry in bloomberg_feed.entries[:5]:  # Top 5 headlines
                    headlines.append(NewsHeadline(
                        title=entry.title,
                        source="Bloomberg",
                        timestamp=getattr(entry, 'published', None)
                    ))
            except Exception as e:
                logger.warning(f"Failed to fetch Bloomberg news: {e}")

            # Limit to 10 total headlines
            headlines = headlines[:10]

            self._set_cached_data(cache_key, headlines)
            return headlines

        except Exception as e:
            logger.error(f"Failed to fetch news headlines: {e}")
            return []

# Global market data service instance
market_service = MarketDataService()

@market_router.get("/status", response_model=MarketStatusResponse)
async def get_market_status():
    """
    Get comprehensive market intelligence status
    DALS-001 compliant: Returns real data or zeros for unavailable services
    """
    try:
        # Fetch all market data concurrently
        indexes, stocks, crypto, news = await asyncio.gather(
            market_service.get_market_indexes(),
            market_service.get_top_stocks(),
            market_service.get_crypto_data(),
            market_service.get_news_headlines()
        )

        return MarketStatusResponse(
            indexes=indexes,
            stocks=stocks,
            crypto=crypto,
            news=news,
            last_updated=datetime.now(timezone.utc).isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to get market status: {e}")
        # Return empty response (DALS-001 compliant)
        return MarketStatusResponse(
            indexes=MarketIndexes(),
            stocks=[],
            crypto=[],
            news=[],
            last_updated=datetime.now(timezone.utc).isoformat()
        )