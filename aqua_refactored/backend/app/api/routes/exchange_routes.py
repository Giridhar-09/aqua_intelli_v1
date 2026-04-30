"""
AquaIntelli - API Routes: Water Futures Exchange
"""
from fastapi import APIRouter, Query
from ...services.exchange_service import get_all_assets, get_order_book, get_price_oracle, generate_trades

router = APIRouter(prefix="/exchange", tags=["Water Exchange"])


@router.get("/assets", summary="All water futures assets",
            description="Get all tradeable water futures with live prices.")
async def list_assets():
    return {"assets": get_all_assets()}


@router.get("/orderbook/{asset_id}", summary="Order book for asset",
            description="Get live order book with bids and asks.")
async def orderbook(asset_id: str):
    return get_order_book(asset_id)


@router.get("/oracle/{asset_id}", summary="AI price oracle",
            description="AI-powered 7/30/90 day price forecast with driving factors.")
async def price_oracle(asset_id: str):
    return get_price_oracle(asset_id)


@router.get("/trades", summary="Recent trades",
            description="Get simulated recent trade feed.")
async def recent_trades(count: int = Query(10, ge=1, le=50)):
    return {"trades": generate_trades(count)}
