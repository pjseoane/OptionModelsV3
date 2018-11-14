
from datetime import datetime
from RofexAPI import PJS_RESTv3 as pjs

def strat1(symb, bPrice,bSize,oPrice,oSize):
    if (bSize < 10):

        print("\n bid Size:\n",bSize)
    return
       # pjs.newSingleOrder("ROFX",symb,bPrice,(10-bSize),"LIMIT","BUY","DAY","555",True)
    #return
    #if (oSize<10):
    #    pjs.newSingleOrder("ROFX", symb, oPrice, (10 - oSize), "LIMIT", "SELL", "DAY", "555")

def MDincoming(msg):
    # Aca es Market Data, esta escuchando novedades
    #Apilar mensajes en una pila por symbol y un thread que lea el ultimo apilado ?

    listaMensajes = []
    subsMDEvents = []
    # subsMDEvents.append(msg)
    print("En MD incoming ****************")

    # sys.stdout.flush()

    timestamp=msg['timestamp']
    symbol = msg['instrumentId']['symbol']


    # Aca hay un problema si no hay bid u offer pq solo viene ['marketData']
    bidMsg = msg['marketData']['BI']
    offerMsg = msg['marketData']['OF']
    # print("BID msg :", bidMsg)
    # print("OFFER msg :",offerMsg)
    if bidMsg == []:
        print("------------------------------------------>No BID detected")
        bid = 0
        bidSize = 0
    else:
        bid = msg['marketData']['BI'][0]['price']
        bidSize = msg['marketData']['BI'][0]['size']
    if offerMsg == []:
        print("------------------------------------------>No OFFER detected")
        offer = 0
        offerSize = 0
    else:
        offer = msg['marketData']['OF'][0]['price']
        offerSize = msg['marketData']['OF'][0]['size']

    strat1(symbol, bid,bidSize,offer,offerSize)





    msgArray = []
    msgArray.append(symbol)

    msgArray.append(bid)
    msgArray.append(bidSize)
    msgArray.append(offer)
    msgArray.append(offerSize)
    listaMensajes.append(msgArray)

    print(symbol, "----->", bid, "/", offer, " size--> ", bidSize, "/", offerSize, "timestamp :", timestamp)
    print("--------------------------------------------------------------------------------------------")

    if (bidSize == 7):
        print("BID Size of ", symbol, "----------------->", bidSize)

    
    # si queremos escribir a un archivo usamos algo asi:
    # filename.write(str(now)+"|"+str(data['marketData']['LA']['price'])+"|"+str(data['marketData']['LA']['size'])+"|"+str(data['marketData']['BI'][0]['price'])+"|"+str(data['marketData']['BI'][0]['size'])+"|"+str(data['marketData']['OF'][0]['price'])+"|"+str(data['marketData']['OF'][0]['size'])+"\n");
    # filename.close()

