from fastapi.encoders import jsonable_encoder

async def Lock(request,reqT,redisT):
    
    response = await reqT.GetJson(request = request)
    if response["status"]:
        try:
            registerID = request.session["RegisterID"]
            
            data = response["data"]
            area = data["area"]
            row = data["row"]
            column = data["column"]
            
            event_id = data["event_id"]
            
            seatLockKey = f"<seatLock>:[{event_id}:{area}:{row}:{column}]"
            userSeatIndexKey = f"<userSeatIndex>:[{registerID}]"
            
            TicketLock_result = redisT.TicketLock(seatLockKey=seatLockKey,userSeatIndexKey=userSeatIndexKey,registerID=registerID)
            return TicketLock_result
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketModule_LockError ! message : [{type(e)} {e}]"}
    return response


async def GetTicketData(request,reqT,sqlT,totpT,redisT):
    
    response = await reqT.GetJson(request = request)
    if response["status"]:
        
        try:
            registerID = request.session["RegisterID"]
            loginID = request.session["UserID"]
            
            data = response["data"]
            event_id = data["event_id"]
            area = data["area"]
            row = data["row"]
            column = data["column"]
            totpcode = data["totpcode_input"]

            GetSecret_result = sqlT.GetSecret(loginID=loginID)
            if not GetSecret_result["status"]:
                return GetSecret_result
            
            secret = GetSecret_result["secret"]
            totpobject = totpT.GetTotpObject(secret)
            
            if totpcode == str(totpobject.now()):
                
                InsertTicketData_result = sqlT.InsertTicketData(registerID=registerID,event_id=event_id,area=area,row=row,column=column)
                if InsertTicketData_result["status"]:
                    
                    TicketSuccess_result = redisT.TicketSuccess(event_id=event_id,registerID=registerID)
                    if not TicketSuccess_result["status"]:
                        return TicketSuccess_result
                    
                    return {"status":True,
                            "notify":"票券資料寫入成功 !"}
                return InsertTicketData_result
            else:
                return {"status":False,
                        "notify":"驗證碼輸入錯誤 !"}
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketModule_GetTicketDataError ! message : [{type(e)} {e}]"}
    return response

async def CheckTicket(request,reqT,redisT):
    
    response = await reqT.GetJson(request = request)
    if response["status"]:
        
        try:
            
            data = response["data"]
            registerID = request.session["RegisterID"]
            event_id = data["event_id"]
            userName = request.session["UserName"]
            
            TicketCheck_result = redisT.TicketCheck(event_id=event_id,registerID=registerID,userName=userName)
            return TicketCheck_result
        
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketModule_CheckTicketError ! message : [{type(e)} {e}]"}
    return response

async def CancelTicket(request,reqT,redisT):
    response = await reqT.GetJson(request = request)
    if response["status"]:
        try:
            registerID = request.session["RegisterID"]
            data = response["data"]
            event_id = data["event_id"]
            area = data["area"]
            row = data["row"]
            column = data["column"]
            seatLockKey = f"<seatLock>:[{event_id}:{area}:{row}:{column}]"
            userSeatIndexKey = f"<userSeatIndex>:[{registerID}]"
            TicketCancel_result = redisT.TicketCancel(seatLockKey=seatLockKey,userSeatIndexKey=userSeatIndexKey)
            if TicketCancel_result["status"]:
                TicketCancel_result["notify"] = f"{seatLockKey} 已釋放 !"
            return TicketCancel_result
        
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketModule_CancelTicketError ! message : [{type(e)} {e}]"}
    return response

async def RestoreTicket(request,redisT):
    try:
        registerID = request.session["RegisterID"]
        userSeatIndexKey = f"<userSeatIndex>:[{registerID}]"
        TicketRestore_result = redisT.TicketRestore(userSeatIndexKey=userSeatIndexKey,registerID=registerID)
        return TicketRestore_result
    except Exception as e:
        return {"status":False,
                "notify":f"TicketModule_RestoreTicketError ! message : [{type(e)} {e}]"}

async def CheckTicketPurchased(request,reqT,sqlT):

    response = await reqT.GetJson(request=request)
    if response["status"]:
        try:
            data = response["data"]
            title = data["title"]
            
            GetEventID_result = sqlT.GetEventID(title=title)
            if GetEventID_result["status"]:
                event_id = GetEventID_result["event_id"]
            else:
                return GetEventID_result
            
            GetPurchasedData_result = sqlT.GetPurchasedData(event_id=event_id)
            
            if GetPurchasedData_result["status"]:
                purchasedData = GetPurchasedData_result["purchasedData"]
            else:
                return GetPurchasedData_result
            return {"status":True,
                    "purchased":jsonable_encoder(purchasedData),
                    "event_id":event_id}
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketModule_CheckTicketPurchasedError ! message : [{type(e)} {e}]"}
    return response