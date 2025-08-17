import redis
from urllib.parse import urlparse

class RedisBase:
    def __init__(self,url):
            self.url = urlparse(url)
            self.r = redis.Redis(host=self.url.hostname,
                                 port=self.url.port,
                                 password=self.url.password,
                                 decode_responses=True)
    def ParseSeatLockKey(self,key):
        key = dict(zip(["event_id","area","row","column"],key.split("[")[1].split("]")[0].split(":")))
        return key
            
    

class RedisTools(RedisBase):
    def __init__(self,URL):
        super().__init__(URL)
    def TicketLock(self,seatLockKey,userSeatIndexKey,registerID):

        try:
            lock = self.r.get(seatLockKey)
            if not lock:
                if not self.r.set(userSeatIndexKey, seatLockKey, nx=True, ex=60):
                    return {"status":False,
                            "notify":"不可多選 !"}
                self.r.set(seatLockKey, registerID , nx=True, ex=60)
                return {"status":True,
                        "time":self.r.pttl(seatLockKey)/1000}
            
            if lock==str(registerID):
                return {"status":True,
                        "time":self.r.pttl(seatLockKey)/1000}
            return {"status":False,"notify":"無法選位 !"}
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketLockError ! message : {type(e)} {e}"}
        
    
    def TicketSuccess(self,event_id,registerID):
        try:
            self.r.lpush(event_id,registerID)
            return {"status":True,
                    "notify":f"RegisterID : {registerID} 已 push 至 Redis 序列 !"}
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketSuccessError ! message : {type(e)} {e}"}
    
    def TicketCheck(self,event_id,registerID,userName):
        try:
            if str(registerID) in self.r.lrange(event_id,0,-1):
                return {"status":False,
                        "notify":f"{userName}您好，每人限購一張，不可重複購票 !"}
            return {"status":True}
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketSuccessError ! message : {type(e)} {e}"}
    
    def TicketCancel(self,seatLockKey,userSeatIndexKey):
        try:
            deleteSeatLockKey = self.r.delete(seatLockKey)
            deleteUserSeatIndexKey = self.r.delete(userSeatIndexKey)
            if deleteSeatLockKey and deleteUserSeatIndexKey:
                return {"status":True,"notify":f"{seatLockKey} & {userSeatIndexKey} 已從 Redis 中刪除 !"}
            else:
                notify = []
                if not deleteSeatLockKey:
                    notify.append(seatLockKey)
                if not deleteUserSeatIndexKey:
                    notify.append(userSeatIndexKey)
                notify = "、".join(notify)
                return {"status":False,"notify":f"{notify} 不存在 !"}
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketCancelError ! message : {type(e)} {e}"}
        
    
    def TicketRestore(self,userSeatIndexKey,registerID):
        try:
            seatLockKey = self.r.get(userSeatIndexKey)
            if not seatLockKey:
                return {"status":False,"notify":"沒有選位資料 !"}
            
            lock = self.r.get(seatLockKey)
            if not lock:
                return {"status":False,"notify":"沒有選位資料 !"}
            
            if lock==str(registerID):
                seat = self.ParseSeatLockKey(seatLockKey)
                return {"status":True,
                        "seat":seat,
                        "time":self.r.pttl(seatLockKey)/1000}
            return {"status":False,"notify":"不同的使用者 !"}
        except Exception as e:
            return {"status":False,
                    "notify":f"TicketRestoreError ! message : {type(e)} {e}"}


