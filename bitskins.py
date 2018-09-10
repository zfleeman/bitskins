import pyotp
import requests as r
import json
import time

class bitSkins:
    
    def __init__(self, api = '', secret = ''):
        self.api = api
        self.secret = secret
        
        self.on_sale = []
        
        self.auth()
        
        self.payload = {
            'api_key':self.api,
            'code':self.token.now(),
        }
        
        self.bids = []
        
        self.api_counter = 0
            
    def auth(self):
        if(len(self.api) < 5):
            self.api = raw_input('API Key: ')
            
        if(len(self.secret) < 2):
            self.secret = raw_input('Secret BitSkin 2FA: ')
        else:
            self.get_token()
        
    def get_token(self):
        self.token = pyotp.TOTP(self.secret)
        
    def api_timer(self):
        self.api_counter += 1
        
        if(self.api_counter == 8):
            self.api_counter = 0
            time.sleep(1)
            
        
    def refresh_payload(self):
        
        self.payload['code'] = self.token.now()
        
        return self.payload
        
    def get_account_balance(self):
        print r.post('https://bitskins.com/api/v1/get_account_balance/', data = self.payload).content
        
    def get_all_item_prices(self):
        self.prices = r.post('https://bitskins.com/api/v1/get_all_item_prices/',self.refresh_payload()).json()['prices']
        
    def get_inventory_with_bid(self, pages = 50, per_page = 480, sort_by = 'price', order = 'desc',
                              market_hash_name = '', min_price = 0, max_price = 1000000, has_stickers = 0,
                              is_stattrak = 0, is_souvenir = 0, show_trade_delayed_items = 0):
        
        self.on_sale = []
        
        self.payload['market_hash_name'] = market_hash_name
        self.payload['per_page'] = per_page
        self.payload['sort_by'] = sort_by
        self.payload['order'] = order
        self.payload['min_price'] = min_price
        self.payload['max_price'] = max_price
        self.payload['has_stickers'] = has_stickers
        self.payload['is_stattrak'] = is_stattrak
        self.payload['is_souvenir'] = is_souvenir
        self.payload['show_trade_delayed_items'] = show_trade_delayed_items
        
        for i in range(1, pages+1):
            self.payload['page'] = i
            
#            res = r.post('https://bitskins.com/api/v1/get_inventory_on_sale/', self.refresh_payload()).json()['data']['items']
            res = r.post('https://bitskins.com/api/v1/get_inventory_on_sale/', self.refresh_payload()).json()['data']

            
            if(len(res) > 0):
                self.on_sale.extend(res)
                
            else:
                break
            #self.api_timer()
        
        return market_hash_name.upper() + ' // ' + str(len(self.on_sale)) + ' items match that search. ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
            
        
    def create_bid(self, skin_name, max_price, max_wear, has_stickers, is_stattrak, is_souvenir, show_trade_delayed_items):
        bid = {
            'market_hash_name':skin_name,
            'max_price':max_price,
            'max_wear':max_wear,
            'stickers':has_stickers,
            'stattrak':is_stattrak,
            'souvenir':is_souvenir,
            'trade_delayed':show_trade_delayed_items
        }
        
        self.bids.append(bid)
        
    def buy_item(self,item_id,price):
        self.payload['item_ids'] = item_id
        self.payload['prices'] = price
        print r.post('https://bitskins.com/api/v1/buy_item', self.refresh_payload()).json()['status']
        
    def go_shopping(self,bid):        
        message = self.get_inventory_with_bid(market_hash_name = bid['market_hash_name'], has_stickers = bid['stickers'], is_stattrak = bid['stattrak'],is_souvenir = bid['souvenir'], show_trade_delayed_items = bid['trade_delayed'])
        
        item_ids = []
        wears = []
        prices = []

        for x in self.on_sale:
            wears.append(float(x['float_value']))
            item_ids.append(x['item_id'])
            prices.append(float(x['price']))

        win_wears = [x for x in wears if x <= bid['max_wear']]
        test_price = [wears.index(w) for w in win_wears]

        for t in test_price:
            if(prices[t] <= bid['max_price']):
                self.buy_item(item_id = item_ids[t], price = prices[t])
                print 'Bought that shit. Item ' + str(item_ids[t]) + ' at $' + str(prices[t]) + '. ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                return False
                    
        return True, message
    
def main():
    creds = open('credentials.txt','r')
    api = creds.readline()
    secret = creds.readline()
    creds.close()
    
    bs = bitSkins(api = api[:-1], secret = secret)
    
    while(True):
        if(raw_input('Create a bid? y/n: ') == 'y'):
            skin_name = raw_input('What is the skin name? ')
            max_price = float(raw_input('What is your max bid price? '))
            max_wear = float(raw_input('Finally, what is the highest wear decimal you will accept? '))
            
            stick = raw_input("Stickers? y/n/eh: ")

            if(stick == 'y'):
                has_stickers = 1
            elif(stick == 'n'):
                has_stickers = -1
            elif(stick == 'eh'):
                has_stickers = 0

            stat = raw_input("StatTrak? y/n/eh: ")

            if(stat == 'y'):
                is_stattrak = 1
            elif(stat == 'n'):
                is_stattrak = -1
            elif(stat == 'eh'):
                is_stattrak = 0

            souv = raw_input("Souvenir? y/n/eh: ")

            if(souv == 'y'):
                is_souvenir = 1
            elif(souv == 'n'):
                is_souvenir = -1
            elif(souv == 'eh'):
                is_souvenir = 0

            td = raw_input("Include trade-delayed items in search? y/n: ")

            if(td == 'y'):
                show_trade_delayed_items = 0
            elif(td == 'n'):
                show_trade_delayed_items = -1        

            bs.create_bid(skin_name, max_price, max_wear, has_stickers, is_stattrak, is_souvenir, show_trade_delayed_items)
            
            
        else:
            break
            
    while(True):
        
        for bid in bs.bids:
            kill = bs.go_shopping(bid)
            if(not kill):
                del bs.bids[bs.bids.index(bid)]
                
        if(len(bs.bids) == 0):
            exit()
            
#if __name__ == '__main__':
#    main()