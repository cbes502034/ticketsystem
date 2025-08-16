from fastapi import FastAPI,Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ProjectTools.SqlTools import SqlTools
from ProjectTools.RequestTools import RequestTools
from ProjectTools.TotpTools import TotpTools
from ProjectTools.RedisTools import RedisTools

from Modules import RegisterModule,LoginModule,IndexModule,LogoutModule,ProfileModule,TicketModule

'''
app = FastAPI()
url = {"mysql":"mysql://root:DdAmmOtQGtxHmxhCiTZTxYmSgrnLlBSk@gondola.proxy.rlwy.net:51385/railway",
       "redis":"redis://default:tIpRCpsuUUNmIOOyqAfMHjlnxLjojRGb@shinkansen.proxy.rlwy.net:46195"}
reqT = RequestTools()
totpT = TotpTools()
sqlT = SqlTools(URL=url["mysql"])
redisT = RedisTools(URL=url["redis"])

KEY = "ticket_key"
app.add_middleware(SessionMiddleware,secret_key=KEY)
'''
import os
from dotenv import load_dotenv
app = FastAPI()
load_dotenv()
url = {"mysql":os.getenv("MYSQLPUBLICURL"),
       "redis":os.getenv("REDISPUBLICURL")}
reqT = RequestTools()
totpT = TotpTools()
sqlT = SqlTools(URL=url["mysql"])
redisT = RedisTools(URL=url["redis"]).r

KEY = "ticket_key"
app.add_middleware(SessionMiddleware,secret_key=KEY)

@app.post("/auth/verify/init")
async def ShowQRcode(request: Request):
    response = await RegisterModule.ShowQRcode(request=request,reqT=reqT,totpT=totpT)
    return JSONResponse(response)

@app.post("/auth/verify/confirm")
async def Register(request: Request):
    response = await RegisterModule.CheckANDRegister(request=request,reqT=reqT,sqlT=sqlT,totpT=totpT)
    return JSONResponse(response)

@app.post("/auth/login")
async def Login(request:Request):
    response = await LoginModule.Check(request=request,reqT=reqT,sqlT=sqlT)
    return JSONResponse(response)

@app.get("/auth/logout")
async def Logout(request:Request):
    response = await LogoutModule.Logout(request=request)
    return JSONResponse(response)

@app.post("/profile")
async def Profile(request:Request):
    response = ProfileModule.GetProfileData(request=request,sqlT=sqlT)
    return JSONResponse(response)
    
@app.get("/auth/user")
async def User(request : Request):
    response = IndexModule.CheckUserLogin(request=request)
    return JSONResponse(response)

@app.post("/ticket/lock")
async def LockTicket(request:Request):
    response = await TicketModule.Lock(request=request,reqT=reqT,redisT=redisT)
    return JSONResponse(response)

@app.post("/ticket")
async def GetTicket(request : Request):
    response = await TicketModule.GetTicketData(request=request,reqT=reqT,sqlT=sqlT,totpT=totpT,redisT=redisT)
    return JSONResponse(response)

@app.post("/ticket/check")
async def CheckTicket(request : Request):
    response = await TicketModule.CheckTicket(request=request,reqT=reqT,redisT=redisT)
    return JSONResponse(response)

@app.post("/ticket/cancel")
async def CancelTicket(request : Request):
    response = await TicketModule.CancelTicket(request=request,reqT=reqT,redisT=redisT)
    return response

@app.post("/ticket/restore")
async def RestoreTicket(request : Request):
    return {"status":True}
    response = await TicketModule.RestoreTicket(request=request,redisT=redisT)
    return response

@app.post("/ticket/availability")
async def GetTicketAvailability(request : Request):
    response = await TicketModule.CheckTicketPurchased(request=request,reqT=reqT,sqlT=sqlT)
    return JSONResponse(response)


app.mount("/", StaticFiles(directory="Frontend", html=True))





