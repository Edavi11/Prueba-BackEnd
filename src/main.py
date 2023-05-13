import requests
from fastapi import FastAPI
from config import API_KEY, StockList

app = FastAPI()

# endpoint para validar alcanzabilidad de la aplicacion
@app.get("/hello")
async def hello():
    return {'message':'es alcanzable'}

# endpoint para obtener el costo total necesario para comprar todos los stocks disponibles
@app.get("/total_cost")
async def get_total_cost():        
        
    # varibale que contendra el costo total a devolver
    total_cost = 0
    
    # realizamos un bucle for para interar y obtener cada precio de nuestra lista de stocks, los sumamos y obtenemos el total
    for stock in StockList:
                
        # definimos la url de la cual obtendremos el valor de cada stock
        url = f"https://financialmodelingprep.com/api/v3/quote/{stock}?apikey={API_KEY}"
            
        # realizarmos la peticion http tipo GET hacia la url establecido y obtenemos el valor en formato JSON
        response = requests.get(url).json()
        
        print(response)
        
        # validamos que vada response sea exitoso
        # if response.status_code != 200:
        #     return {"error": "no se pudo obtener el precio de stock en estos momentos..."}
                    
        # validamos que los response obtenidos anteriormente nos devuelvan la data correctamente y sino es asi, simplemente continuamos
        if len(response) == 0:
            continue
        
        # almacenamos el precio de cada stock 
        price = response[0]["price"]
                
        # suamos y obtenemos el total de los precios de los stocks
        total_cost += price
        
    # devolvemos el valor del costo total necesario para comprar todos los stocks disponibles 
    return {"total_cost": round(total_cost, 2)}


@app.get("/portfolio")
async def get_portfolio(amount: float):
    
    url = f"https://financialmodelingprep.com/api/v3/quote-short/{','.join(StockList)}?apikey={API_KEY}"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "no se pudo obtener los precios de los stocks"}
    
    stock_data = response.json()
    
    sorted_stocks = sorted(stock_data, key=lambda x: x["price"], reverse=True)
    
    portfolio = {}
    for stock in sorted_stocks:
        if amount <= 0:
            break
        stock_price = stock["price"]
        stock_symbol = stock["symbol"]
        
        
        if amount >= stock_price:
            shares = int(amount / stock_price)
            amount -= shares * stock_price
            portfolio[stock_symbol] = shares
            
    if amount > 0:
        
        if len(portfolio) == len(StockList):
            # All stocks were purchased with the exact amount provided
            portfolio[sorted_stocks[-1]["symbol"]] += amount / sorted_stocks[-1]["price"]
        else:
            
            # Not all stocks could be purchased with the amount provided, so we need to adjust the amounts
            remaining_stocks = set(StockList) - set(portfolio.keys())
            remaining_stocks_prices = {s["symbol"]: s["price"] for s in sorted_stocks if s["symbol"] in remaining_stocks}
            while amount > 0 and remaining_stocks_prices:
                next_stock_symbol = max(remaining_stocks_prices, key=remaining_stocks_prices.get)
                next_stock_price = remaining_stocks_prices[next_stock_symbol]
                shares = int(amount / next_stock_price)
                if shares > 0:
                    amount -= shares * next_stock_price
                    portfolio[next_stock_symbol] = shares
                del remaining_stocks_prices[next_stock_symbol]
            
    return {"portfolio": portfolio, "remaining_amount": round(amount, 2)}
