from fastapi import FastAPI, HTTPException, Depends
from routers.stock_routers import router as stock_router
from routers.indicators_routers import router as indicators_router
from routers.llm_routers import router as llm_router
import pandas as pd

api = FastAPI()

# Load data
stockPrices = pd.read_csv('data/stockPrices.csv')
stockPrices = stockPrices[stockPrices['price'] != "{'$numberDouble': 'NaN'}"]
stockInfo = pd.read_csv('data/stockInfo.csv')

dollar = pd.read_csv('data/dollar.csv')
selic = pd.read_csv('data/selic.csv')
ipca = pd.read_csv('data/ipca.csv')


api.state.stockPrices = stockPrices
api.state.stockInfo = stockInfo

api.state.dollar = dollar
api.state.selic = selic
api.state.ipca = ipca

api.include_router(stock_router)
api.include_router(indicators_router)
api.include_router(llm_router)


@api.get("/")
def read_root():
    return {"message": "API rodando!"}


@api.get("/superior_ao_dolar")
def superior_ao_dolar():
    stockPrices = api.state.stockPrices
    dollar = api.state.dollar
    stockPrices = stockPrices[stockPrices['year-month'].isin(dollar['year-month'])]
    stockPrices = stockPrices.groupby('ticker').apply(lambda x: x['price'].mean() > dollar['price'].mean())
    return stockPrices.to_json()

