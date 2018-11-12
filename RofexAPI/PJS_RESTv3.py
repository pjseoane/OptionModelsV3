
import requests
import simplejson

# User y Password para la API - Utilizamos un objeto Session para loguearnos para que se mantega la cookie de sesion en las proximas llamadas
initialized = False
islogin = False
user = ""
password = ""
activeEndpoint = ""
activeWSEndpoint = ""
account = ""
token = ""
verifyHTTPs = False
symbol=""
marketId=""
CFIcode=""
segments=""
cancelPrevious=False
iceberg=False


s = requests.Session()



# Endpoint
#endpointDemo = "http://demo-api.primary.com.ar/"
#wsEndpointDemo="ws://demo-api.primary.com.ar/"
#historyOHLC_endpoint = "http://h-api.primary.com.ar/MHD/TradesOHLC/{s}/{fi}/{ff}/{hi}/{hf}"
def suscribirContratos():
    contracts=[]
    contracts.append("RFX20Dic18")
    contracts.append("DoDic18")
    return contracts


def setURLs():
    global endpointDemo, wsEndpointDemo, historyOHLC_endpoint
    endpointDemo = "http://demo-api.primary.com.ar/"
    wsEndpointDemo = "ws://demo-api.primary.com.ar/"
    historyOHLC_endpoint = "http://h-api.primary.com.ar/MHD/TradesOHLC/{s}/{fi}/{ff}/{hi}/{hf}"

    print("setURLs Ok...")

#
def init(userParam, passwordParam, accountParam, entornoParam, verifyHTTPsParam=False):
    global user, password, account, activeEndpoint, initialized, activeWSEndpoint, verifyHTTPs
    user = userParam
    password = passwordParam
    account = accountParam
    verifyHTTPs = verifyHTTPsParam
    if entornoParam == 1:
        activeEndpoint = endpointDemo
        activeWSEndpoint = wsEndpointDemo
        print ("init() Ok...")
    else:
        print ("Entorno incorrecto")
    initialized = True


def requestAPI(url):
    if(not login): raise PMYAPIException("Usuario no Autenticado.")
    else:
        global token
        headers = {'X-Auth-Token': token}
        r = requests.get(url, headers=headers, verify=verifyHTTPs)
        return r

# Fix API Parameter
marketID='ROFX'
timeInForce='Day'


class PMYAPIException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg



def login():    
    
    #Validamos que se inicializaron los parametros 
    global initialized, activeEndpoint, islogin, token
    success=False
    if(not initialized): raise PMYAPIException("Parametros no inicializados.")
    if(not islogin):
        url = activeEndpoint+"auth/getToken"
        headers = {'X-Username': user, 'X-Password': password}
        loginResponse = s.post(url, headers=headers, verify=False) 
        # Checkeamos si la respuesta del request fue correcta, un ok va a ser un response code 200 (OK)
        if(loginResponse.ok):        
            token = loginResponse.headers['X-Auth-Token']
            success = True
            print("login() OK...")
        else:   
            print("Request Error.")
            success = False
        islogin=success   
    else:
        print ("Ya estamos logueados")
        success = True
    return success


def listaSegmentosDisp():
    url = activeEndpoint + "rest/segment/all"
    r = requestAPI(url)
    return simplejson.loads(r.content)


#2
def instrumentos():
    url = activeEndpoint + "rest/instruments/all"
    r = requestAPI(url)
    return simplejson.loads(r.content)


def instrumentsDetailsAll():
    url = activeEndpoint + "rest/instruments/details"
    r = requestAPI(url)
    return simplejson.loads(r.content)


def instrumentDetail(symbol, marketId):
    url = activeEndpoint + "rest/instruments/detail?symbol="+symbol+"&marketId="+marketId
    r = requestAPI(url)
    return simplejson.loads(r.content)


def instrumentsByCFICode(CFIcode):
    url = activeEndpoint + "rest/instruments/byCFICode?CFICode="+CFIcode
    r = requestAPI(url)
    return simplejson.loads(r.content)


def instrumentsBySegments(segments):
    url = activeEndpoint + "rest/instruments/bySegment?MarketSegmentID="+segments+"&MarketID=ROFX"
    r = requestAPI(url)
    return simplejson.loads(r.content)

def newSingleOrder(marketId,symbol,price,orderQty,ordType,side,timeInForce,account,cancelPrevious):
    url = activeEndpoint+"rest/order/newSingleOrder?marketId="+marketId+"&symbol="+symbol+"&price="+price+"&orderQty="+orderQty+"&ordType="+ordType+"&side="+side+"&timeInForce="+timeInForce+"&account="+account+"&cancelPrevious="+cancelPrevious 
   
    # &iceberg=False&displayQty=0"   
    r = requestAPI(url)
    return simplejson.loads(r.content)


def newIcebergOrder(marketId,symbol,price,orderQty,ordType,side,timeInForce,account,cancelPrevious,iceberg,displayQty):
    url = activeEndpoint+"rest/order/newSingleOrder?marketId="+marketId+"&symbol="+symbol+"&price="+price+"&orderQty="+orderQty+"&ordType="+ordType+"&side="+side+"&timeInForce="+timeInForce+"&account="+account+"&cancelPrevious="+cancelPrevious+"&iceberg="+iceberg+"&displayQty="+displayQty 
   
    # &iceberg=False&displayQty=0"   
    r = requestAPI(url)
    return simplejson.loads(r.content)


def newGTDOrder(marketId,symbol,price,orderQty,ordType,side,timeInForce,account,expireDate):
    url = activeEndpoint+"rest/order/newSingleOrder?marketId="+marketId+"&symbol="+symbol+"&price="+price+"&orderQty="+orderQty+"&ordType="+ordType+"&side="+side+"&timeInForce=GTD"+"&account="+account+"&expireDate="+expireDate
   
    r = requestAPI(url)
    return simplejson.loads(r.content)


def replaceOrderById(clOrdId,proprietary,price, orderQty):
    url = activeEndpoint+"rest/order/replaceById?clOrdId="+clOrdId+"&proprietary="+proprietary+"&price="+price+"&orderQty="+orderQty
   
    r = requestAPI(url)
    return simplejson.loads(r.content)


def cancelOrderById(clOrdId,proprietary):
    url = activeEndpoint+"rest/order/cancelById?clOrdId="+clOrdId+"&proprietary="+proprietary
   
    r = requestAPI(url)
    return simplejson.loads(r.content)


def consultarUltEstadoOrderById(clOrdId,proprietary):
    url = activeEndpoint+"rest/order/id?clOrdId="+clOrdId+"&proprietary="+proprietary
   
    r = requestAPI(url)
    return simplejson.loads(r.content)


def consultarAllEstadoOrderById(clOrdId,proprietary):
    url = activeEndpoint+"rest/order/allById?clOrdId="+clOrdId+"&proprietary="+proprietary
   
    r = requestAPI(url)
    return simplejson.loads(r.content)


def consultarOrden(orderId):
    url = activeEndpoint+"rest/order/byOrderId?orderId="+orderId
   
    r = requestAPI(url)
    return simplejson.loads(r.content)

def consultarOrdenesActivas(accountId):
    url = activeEndpoint+"rest/order/actives?accountId="+accountId
   
    r = requestAPI(url)
    #return r.content
    return simplejson.loads(r.content)


def consultarOrdenesOperadas(accountId):
    url = activeEndpoint+"rest/order/filleds?accountId="+accountId
   
    r = requestAPI(url)
    return simplejson.loads(r.content)

def consultarOrdenesAllClientOrder(accountId):
    url = activeEndpoint+"rest/order/all?accountId="+accountId
   
    r = requestAPI(url)
    return simplejson.loads(r.content)


def consultarOrdenExecutionId(execId):
    url = activeEndpoint+"rest/order/byExecId?execId="+execId
   
    r = requestAPI(url)
    return simplejson.loads(r.content)


def getMarketData(marketId,symbol,p1,p2,p3,p4,p5,p6,p7,depth):
    url = activeEndpoint+"rest/marketdata/get?marketId="+marketId+"&symbol="+symbol+"&entries="+p1+","+p2+","+p3+","+p4+","+p5+","+p6+","+p7+"&depth="+depth                            
   
    r = requestAPI(url)
    
    return simplejson.loads(r.content)

def getMarketDataHist(marketId,symbol,date):
    url = activeEndpoint+"rest/data/getTrades?marketId="+marketId+"&symbol="+symbol+"&date="+date                            
   
    r = requestAPI(url)
    
    return simplejson.loads(r.content)


def getMarketDataHistRange(marketId,symbol,dateFrom,dateTo):
    url = activeEndpoint+"rest/data/getTrades?marketId="+marketId+"&symbol="+symbol+"&dateFrom="+dateFrom+"&dateTo="+dateTo                            
   
    r = requestAPI(url)
    
    return simplejson.loads(r.content)

