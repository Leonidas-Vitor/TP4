from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional
#from bson.json_util import dumps
import pandas as pd
import os

router = APIRouter(
    prefix="/stock",
)

# Solução Local


@router.get("/")
def status():
    return "Stock API is running!"

class ValorizationGetModel(BaseModel):
    ticker: Optional[str] = Field(None, alias=['ticker','etiqueta'])#, default=None)
    year_month: Optional[str] = Field('2020-01', alias='data', pattern='[0-9]{4}-[0-9]{2}')
    
    class Config:
        populate_by_name = True

@router.get("/valorizationt")
def Teste(teste : ValorizationGetModel = Depends()):
    return teste.ticker

@router.get("/valorization")
def GetCollectionData(request: Request, valorizationGetModel : ValorizationGetModel = Depends()):
    '''
    Retorna a valorização de um ativo em relação a um determinado mês.
    Se o ticker for None, retorna a valorização de todos os ativos em relação a um determinado mês.
    '''

    stockPrices = request.app.state.stockPrices

    if valorizationGetModel.ticker is not None and  valorizationGetModel.ticker not in stockPrices['ticker'].unique():
        raise HTTPException(status_code=404, detail='Erro 404: Ticker não encontrado')
    
    elif valorizationGetModel.ticker is None:
        df = stockPrices.copy()
        df_ticker = pd.DataFrame()
        df_filtered = pd.DataFrame()
        for ticker in df['ticker'].unique():
            referenceValue = df[(df['ticker'] == ticker) & (df['year-month'] == valorizationGetModel.year_month)]['price']
            ##SE O TICKER NÃO EXISTIR NO MÊS, RETORNA ERRO
            try:
                referenceValue = float(referenceValue.values[0])
            except:
                referenceValue = float(df[(df['ticker'] == ticker) & (df['price'] is not None)].iloc[0]['price'])

            year_month_index = df[df['year-month'] == valorizationGetModel.year_month].index[0]
                
            df_ticker = df[(df['ticker'] == ticker) & (df.index > year_month_index)].copy()
            df_ticker['valorization'] = (df_ticker['price'].apply(lambda x: float(x) / referenceValue - 1) * 100)
            df_ticker = df_ticker[['ticker', 'year-month', 'price', 'valorization']]
            df_filtered = pd.concat([df_filtered, df_ticker])
        return df_filtered.to_json()
    
    else:
        referenceValue = stockPrices[(stockPrices['ticker'] == valorizationGetModel.ticker) & (stockPrices['year-month'] == valorizationGetModel.year_month)]['price']
        referenceValue = float(referenceValue.values[0])
        year_month_index = stockPrices[stockPrices['year-month'] == valorizationGetModel.year_month].index[0]
        
        df_filtered = stockPrices[(stockPrices['ticker'] == valorizationGetModel.ticker) & (stockPrices.index > year_month_index)].copy()
        df_filtered['valorization'] = df_filtered['price'].apply(lambda x: float(x) / referenceValue - 1) * 100

        df_filtered = df_filtered[['ticker', 'year-month', 'valorization']]
        return df_filtered.to_json()


class StockInfoGetModel(BaseModel):
    ticker: str = Field(alias='etiqueta', default=None)
    
    class Config:
        populate_by_name = True


@router.get("/info/")
def GetCollectionData(request: Request,  stockInfoGetModel : StockInfoGetModel = Depends()):
    '''
    Retorna informações de um ativo.
    Se o ticker for None, retorna informações de todos os ativos.
    '''

    stockInfo = request.app.state.stockInfo
    
    if stockInfoGetModel.ticker is not None and  stockInfoGetModel.ticker not in stockInfo['ticker'].unique():
        raise HTTPException(status_code=404, detail='Erro 404: Ticker não encontrado')
    
    elif stockInfoGetModel.ticker is None:
        return stockInfo.to_json(orient='records')
    
    else:
        return stockInfo[stockInfo['ticker'] == stockInfoGetModel.ticker].to_json(orient='records')