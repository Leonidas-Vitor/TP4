from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional
from bson.json_util import dumps
import pandas as pd
import os


router = APIRouter(
    prefix="/indicators",
)


@router.get("/")
def status():
    return "Indicators API is running!"
    

class IndicatorGetModel(BaseModel):
    year_month: Optional[str] = Field('2020-01', alias='data', pattern='[0-9]{4}-[0-9]{2}')
    
    class Config:
        populate_by_name = True

@router.get("/dollar/")
def GetDollarData(request: Request, dollarGetModel : IndicatorGetModel = Depends()):
    '''
    Retorna a cotação do dólar em relação a um determinado mês.
    '''
    dollar = request.app.state.dollar
    if dollarGetModel.year_month not in dollar['year-month'].unique():
        raise HTTPException(status_code=404, detail='Erro 404: Mês não encontrado')
    
    return dollar[dollar['year-month'] == dollarGetModel.year_month].to_json(orient='records')

#----------------------------------------------

@router.get("/selic/")
def GetSelicData(request: Request, selicGetModel : IndicatorGetModel = Depends()):
    '''
    Retorna a taxa Selic em relação a um determinado mês.
    '''
    selic = request.app.state.selic
    if selicGetModel.year_month not in selic['year-month'].unique():
        raise HTTPException(status_code=404, detail='Erro 404: Mês não encontrado')
    
    return selic[selic['year-month'] == selicGetModel.year_month].to_json(orient='records')

#----------------------------------------------

@router.get("/ipca/")
def GetIpcaData(request: Request, ipcaGetModel : IndicatorGetModel = Depends()):
    '''
    Retorna o IPCA em relação a um determinado mês.
    '''
    ipca = request.app.state.ipca
    if ipcaGetModel.year_month not in ipca['year-month'].unique():
        raise HTTPException(status_code=404, detail='Erro 404: Mês não encontrado')
    
    return ipca[ipca['year-month'] == ipcaGetModel.year_month].to_json(orient='records')

#----------------------------------------------


@router.get("/dollar/valorization/")
def GetDollarVariationData(request: Request, dollarGetModel : IndicatorGetModel = Depends()):
    '''
    Retorna a variação do dólar em relação a um determinado mês.
    '''
    dollar = request.app.state.dollar
    if dollarGetModel.year_month not in dollar['year-month'].unique():
        raise HTTPException(status_code=404, detail='Erro 404: Mês não encontrado')
    
    year_month_index = dollar[dollar['year-month'] == dollarGetModel.year_month].index[0]
    df = dollar[dollar.index > year_month_index].copy()
    df['valorization'] = (df['price'] / dollar[dollar['year-month'] == dollarGetModel.year_month]['price'].values[0] - 1) * 100
    return df.to_json(orient='records')

#----------------------------------------------

@router.get("/selic/accumulated/")
def GetSelicAccumulatedData(request: Request, selicGetModel : IndicatorGetModel = Depends()):
    '''
    Retorna a taxa Selic acumulada em relação a um determinado mês.
    '''
    selic = request.app.state.selic
    if selicGetModel.year_month not in selic['year-month'].unique():
        raise HTTPException(status_code=404, detail='Erro 404: Mês não encontrado')
    
    year_month_index = selic[selic['year-month'] == selicGetModel.year_month].index[0]
    df = selic[selic.index > year_month_index].copy()
    df['accumulated'] = df.cumsum()
    return df.to_json(orient='records')

#----------------------------------------------


@router.get("/ipca/accumulated/")
def GetIpcaAccumulatedData(request: Request, ipcaGetModel : IndicatorGetModel = Depends()):
    '''
    Retorna o IPCA acumulado em relação a um determinado mês.
    '''
    ipca = request.app.state.ipca
    if ipcaGetModel.year_month not in ipca['year-month'].unique():
        raise HTTPException(status_code=404, detail='Erro 404: Mês não encontrado')
    
    year_month_index = ipca[ipca['year-month'] == ipcaGetModel.year_month].index[0]
    df = ipca[ipca.index > year_month_index].copy()
    df['accumulated'] = df.cumsum()
    return df.to_json(orient='records')