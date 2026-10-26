from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from .simulation import run
app=FastAPI(title='AeroMapper AI · synthetic survey lab')
app.add_middleware(CORSMiddleware,allow_origins=['http://127.0.0.1:5105'],allow_methods=['GET','POST'],allow_headers=['Content-Type'])
class Mission(BaseModel):
 seed:int=Field(default=2000,ge=0,le=100000)
 budget:float=Field(default=220,ge=40,le=600)
 family:str='test'
@app.get('/api/health')
def health():return {'status':'ok','hardware_connected':False}
@app.post('/api/compare')
def compare(req:Mission):
 if req.family not in ['test','ood']:raise HTTPException(422,'family must be test or ood')
 return {p:run(req.seed,p,req.budget,req.family) for p in ['lawnmower','adaptive']}
build=Path(__file__).resolve().parents[1]/'frontend/dist'
if build.exists():app.mount('/',StaticFiles(directory=build,html=True),name='frontend')
