
from datetime import datetime
def MDincoming(msg):
    # Aca es Market Data, esta escuchando novedades
    listaMensajes = []
    # subsMDEvents.append(msg)
    print("----------------------------------------------")

    
    # print("Mensajes:---->", len(subsMDEvents))
    #global mensajes
    #mensajes=0
    #mensajes += 1
    #print("Mensajes:---->", mensajes)

    print("En MD incoming")
    """
    # sys.stdout.flush()
    now = datetime.now()
    print(str(now), msg)

    # print("before processinf msg:...")
    symbol = msg['instrumentId']['symbol']

    # print (symbol)

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

    msgArray = []
    msgArray.append(symbol)

    msgArray.append(bid)
    msgArray.append(bidSize)
    msgArray.append(offer)
    msgArray.append(offerSize)
    listaMensajes.append(msgArray)

    print(symbol, "----->", bid, "/", offer, " SIZE--> ", bidSize, "/", offerSize)
    print("------------------------------------------------------")

    if (bidSize == 7):
        print("BID Size of ", symbol, "----------------->", bidSize)

    
    # si queremos escribir a un archivo usamos algo asi:
    # filename.write(str(now)+"|"+str(data['marketData']['LA']['price'])+"|"+str(data['marketData']['LA']['size'])+"|"+str(data['marketData']['BI'][0]['price'])+"|"+str(data['marketData']['BI'][0]['size'])+"|"+str(data['marketData']['OF'][0]['price'])+"|"+str(data['marketData']['OF'][0]['size'])+"\n");
    # filename.close()
"""
