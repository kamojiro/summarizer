from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI(
    title="基本的なFastAPIサーバー",
    description="リクエスト・レスポンスの基本的な例を提供するAPIサーバー",
    version="0.1.0"
)

# POSTリクエスト用のデータモデルを定義
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# データベースの代わりに使用する簡易的なアイテムストレージ
fake_items_db = [
    {"item_id": 1, "name": "ノートパソコン", "price": 100000},
    {"item_id": 2, "name": "スマートフォン", "price": 80000},
    {"item_id": 3, "name": "タブレット", "price": 60000},
    {"item_id": 4, "name": "イヤホン", "price": 15000},
    {"item_id": 5, "name": "マウス", "price": 5000},
]

# ルートパスへのGETリクエスト
@app.get("/")
def read_root():
    return {"message": "こんにちは！FastAPIへようこそ！"}

# パスパラメータを使用したGETリクエスト
@app.get("/items/{item_id}")
def read_item(item_id: int):
    for item in fake_items_db:
        if item["item_id"] == item_id:
            return item
    return {"error": "アイテムが見つかりません"}

# クエリパラメータを使用したGETリクエスト
@app.get("/items/")
def read_items(skip: int = 0, limit: int = Query(default=10, le=100)):
    return fake_items_db[skip : skip + limit]

# リクエストボディを使用したPOSTリクエスト
@app.post("/items/")
def create_item(item: Item):
    # 税込み価格を計算
    price_with_tax = item.price
    if item.tax:
        price_with_tax = item.price * (1 + item.tax)
    
    # 新しいアイテムを作成
    new_item = {
        "item_id": len(fake_items_db) + 1,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "price_with_tax": price_with_tax
    }
    
    # アイテムをデータベースに追加（実際のアプリケーションではデータベースに保存）
    fake_items_db.append(new_item)
    
    return new_item

# サーバー起動用のコード
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
