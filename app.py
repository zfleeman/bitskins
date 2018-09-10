from flask import Flask, request, render_template
import bitskins
import pandas as pd
app = Flask(__name__)

creds = open('credentials.txt','r')
api = creds.readline()
secret = creds.readline()
creds.close()

bs = bitskins.bitSkins(api=api, secret=secret)

@app.route('/', methods=['POST','GET'])
def form(bt = None, nb = None, bid_blocks = None):
    
    if request.method == 'POST':
        if request.form['sub'] == 'Create Bid':
            print 'bidding'
            bs.create_bid(
                skin_name = request.form['skin_name'], 
                max_price = request.form['max_price'], 
                max_wear = request.form['max_wear'], 
                has_stickers = request.form['stickers'], 
                is_stattrak = request.form['stattrak'], 
                is_souvenir = request.form['souv'], 
                show_trade_delayed_items = request.form['td']
            )
            return render_template('bid_form.html', bt = pd.DataFrame(bs.bids).to_html(index = False))
        
        if request.form['sub'] == 'Shop Bids':
            print "shopping"
            bid_blocks = []
            num_bids = len(bs.bids)

            #while True:
            for bid in bs.bids:
                bid_block = '\n{skin_name}\n{search_ind}'.format(skin_name=bid['market_hash_name'].upper(),search_ind='Searching...')
                bid_blocks.append(bid_block)

            return render_template('bid_form.html', bt = pd.DataFrame(bs.bids).to_html(index = False), bid_blocks = bid_blocks)
    
    return render_template('bid_form.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404