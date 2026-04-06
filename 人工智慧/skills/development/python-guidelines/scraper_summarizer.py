import logging
import asyncio
from typing import Protocol, List, Optional
from dataclasses import dataclass, field
import httpx
from bs4 import BeautifulSoup
from pydantic_settings import BaseSettings

# --- 1. 配置與日誌規範 (Ref: env.md, core.md) ---
class Settings(BaseSettings):
    """
    強型別配置類別。
    """
    LOG_LEVEL: str = "INFO"
    TIMEOUT: int = 10
    TARGET_URL: str = "https://www.cnyes.com"

settings = Settings()

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- 2. 領域模型與異常定義 (Ref: core.md) ---
class ScrapingError(Exception):
    """自定義爬蟲異常。"""
    pass

@dataclass(frozen=True)
class Article:
    """不可變的文章資料模型。"""
    title: str
    content_snippet: str
    link: str

@dataclass(frozen=True)
class SummaryReport:
    """最終產出的報告模型。"""
    title: str
    summary: str
    analysis: str

# --- 3. 介面定義 (Ref: core.md - Protocol) ---
class ScraperProtocol(Protocol):
    async def fetch_articles(self, url: str) -> List[Article]:
        ...

class AnalyzerProtocol(Protocol):
    def analyze(self, article: Article) -> SummaryReport:
        ...

# --- 4. 具體實作 (Ref: core.md - Resilience) ---
class AnueScraper:
    """針對鉅亨網的非同步爬蟲實作。"""
    
    async def fetch_articles(self, url: str) -> List[Article]:
        articles: List[Article] = []
        try:
            async with httpx.AsyncClient(timeout=settings.TIMEOUT) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                # 模擬擷取頭條 (實際選擇器需根據網頁結構動態調整)
                headlines = soup.select("h3")[:5] 
                
                for item in headlines:
                    title = item.get_text(strip=True)
                    # 這裡簡化處理，實際開發會進一步抓取全文
                    articles.append(Article(
                        title=title,
                        content_snippet="[內容擷取中...]",
                        link=url
                    ))
            return articles
        except httpx.HTTPError as e:
            logger.error(f"HTTP 請求失敗: {e}", exc_info=True)
            raise ScrapingError(f"無法抓取網頁: {url}") from e

class MacroAnalyzer:
    """
    資深經濟宏觀分析實作。
    這裡作為範例，會根據 Article 內容產出專業分析。
    """
    
    def analyze(self, article: Article) -> SummaryReport:
        # 在實際應用中，此處會串接 LLM API (如 Gemini/OpenAI)
        # 本範例展示其結構化輸出的邏輯
        summary = f"針對「{article.title}」的深度摘要 (約 300 字內容略)..."
        analysis = (
            "【宏觀經濟分析】\n"
            "1. 供需結構：從產能與市場需求觀察，該動態反映了供應鏈的重組趨勢。\n"
            "2. 貨幣政策影響：高利率環境下，資本支出偏向科技權值股。\n"
            "3. 系統性風險：地緣政治仍是目前市場最大的變數。"
        )
        return SummaryReport(title=article.title, summary=summary, analysis=analysis)

# --- 5. 核心執行邏輯 (Ref: core.md - Logging) ---
async def main() -> None:
    scraper: ScraperProtocol = AnueScraper()
    analyzer: AnalyzerProtocol = MacroAnalyzer()
    
    try:
        logger.info(f"開始抓取目標網站: {settings.TARGET_URL}")
        articles = await scraper.fetch_articles(settings.TARGET_URL)
        
        reports: List[SummaryReport] = []
        for art in articles:
            report = analyzer.analyze(art)
            reports.append(report)
            
            # 符合使用者要求的輸出格式
            print(f"# 主題: {report.title}")
            print(f"# 內容: {report.summary}")
            print(f"# 分析: {report.analysis}")
            print("-" * 30)
            
    except ScrapingError:
        logger.critical("應用程式因爬蟲錯誤終止", exc_info=True)
    except Exception as e:
        logger.error(f"非預期錯誤: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
