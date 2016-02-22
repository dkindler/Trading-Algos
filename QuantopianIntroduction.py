# The purpose of this algo was to play around with the Quantopian API
# in order to get fimiliar with it. 

def initialize(context):
    context.limit = 10
    context.stop_price_percent = 0.005
    
    context.pe_max = 14
    context.pe_min = 11
    
    context.pb_max = 2
    
    schedule_function(rebalance, date_rule = date_rules.every_day(), time_rule = time_rules.market_open())

def before_trading_start(context, data):
    context.fundamentals = get_fundamentals(
        query(
            fundamentals.valuation_ratios.pb_ratio,
            fundamentals.valuation_ratios.pe_ratio
        )
        .filter(fundamentals.valuation_ratios.pe_ratio < context.pe_max)
        .filter(fundamentals.valuation_ratios.pb_ratio < context.pb_max)
        .order_by(fundamentals.valuation.market_cap.desc())
        .limit(context.limit)
    )
    update_universe(context.fundamentals.columns.values)
    
def handle_data(context, data):
    cash = context.portfolio.cash
    cur_positions = context.portfolio.positions
    
    for stock in data:
        cur_position = cur_positions[stock].amount
        price = data[stock].price
        stop_price = price - (price * context.stop_price_percent)
        plausible_investment = cash / context.limit
        
        share_amount = int(plausible_investment / price)
        
        try:
            if (price < plausible_investment):
                if (cur_position == 0) and (context.fundamentals[stock]['pe_ratio'] < context.pe_min):
                    order(stock, share_amount, style = StopOrder(stop_price))
                
        except Exception as e:
            print(str(e))

def rebalance(context, data):
    for stock in context.portfolio.positions:
        if stock not in context.fundamentals and stock in data:
            order_target(stock, 0)
