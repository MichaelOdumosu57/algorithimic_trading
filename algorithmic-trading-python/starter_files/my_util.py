import os
import math
def local_deps():
    import sys
    if sys.platform == "win32":
        sys.path.append(sys.path[0] + ".\\site-packages\\windows")
    elif sys.platform =="linux":
        sys.path.append(sys.path[0] + "./site-packages/linux")    
local_deps()


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]   
        
def calc_shares_to_buy(final_dataframe):

    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        calc_shares_to_buy(final_dataframe)
        return
        
    position_size = float(portfolio_size) / len(final_dataframe.index)
    for i in range(0, len(final_dataframe['Ticker'])):
        final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])
