from dotenv import load_dotenv
from fastapi import APIRouter, Depends

from services.rss_service import RSSService

load_dotenv()


# ルーターの作成
router = APIRouter(
    prefix="/rss",
    tags=["rss"],
)


@router.get("/entries")
async def get_rss_entries(
    rss_service: RSSService = Depends(RSSService),
):
    return rss_service.get_rss_feed_urls()
