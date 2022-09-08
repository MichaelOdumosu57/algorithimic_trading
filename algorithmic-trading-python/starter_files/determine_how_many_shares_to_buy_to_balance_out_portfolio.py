from glob import glob
import os
def local_deps():
    import sys
    if sys.platform == "win32":
        sys.path.append(sys.path[0] + ".\\site-packages\\windows")
    elif sys.platform =="linux":
        sys.path.append(sys.path[0] + "./site-packages/linux")    
local_deps()


import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math 
from my_secrets import IEX_CLOUD_API_TOKEN

csv = "{}\\{}".format(os.getcwd(),"sp_500_stocks.csv")
stocks = pd.read_csv(csv)
print(stocks)

 
data = None;
final_dataframe = None;
my_columns = None;
def get_appl_info():
  symbol='AAPL'
  api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
  global data
  data = requests.get(api_url).json()
  

def init_dataframe():
  global my_columns
  my_columns = ['Ticker', 'Price','Market Capitalization', 'Number Of Shares to Buy']
  global final_dataframe
  final_dataframe = pd.DataFrame(columns = my_columns)  

def update_dataframe():
  global stocks
  for symbol in stocks['Ticker'][:5]:
      api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
      data = requests.get(api_url).json()
      global final_dataframe
      final_dataframe = final_dataframe.append(
                                          pd.Series([symbol, 
                                                    data['latestPrice'], 
                                                    data['marketCap'], 
                                                    'N/A'], 
                                                    index = my_columns), 
                                          ignore_index = True)
      
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]





def batch_api_update_dataframe():
  symbol_groups = list(chunks(stocks['Ticker'], 100))
  symbol_strings = []
  for i in range(0, len(symbol_groups)):
      symbol_strings.append(','.join(symbol_groups[i]))
  
  global final_dataframe    
  final_dataframe = pd.DataFrame(columns = my_columns)
  for symbol_string in symbol_strings:
      
      batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
      data = requests.get(batch_api_call_url).json()
      for symbol in symbol_string.split(','):
          try:
            final_dataframe = final_dataframe.append(
              pd.Series([symbol, 
                        data[symbol]['quote']['latestPrice'], 
                        data[symbol]['quote']['marketCap'], 
                        'N/A'], 
                        index = my_columns), 
              ignore_index = True)
          except: 
            None
          
      
  print(final_dataframe)  
  

portfolio_size = ""  
def calculate_shares_to_buy():
  global portfolio_size
  portfolio_size = input("Enter the value of your portfolio:")

  try:
      val = float(portfolio_size)
  except ValueError:
      print("That's not a number! \n Try again:")
      calculate_shares_to_buy() 
      
  position_size = float(portfolio_size) / len(final_dataframe.index)
  for i in range(0, len(final_dataframe['Ticker'])-1):
      final_dataframe.loc[i, 'Number Of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])
  print(final_dataframe) 
  
def output_new_data():
  writer = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter')
  final_dataframe.to_excel(writer, sheet_name='Recommended Trades', index = False)  
  
  background_color = '#0a0a23'
  font_color = '#ffffff'

  string_format = writer.book.add_format(
          {
              'font_color': font_color,
              'bg_color': background_color,
              'border': 1
          }
      )

  dollar_format = writer.book.add_format(
          {
              'num_format':'$0.00',
              'font_color': font_color,
              'bg_color': background_color,
              'border': 1
          }
      )

  integer_format = writer.book.add_format(
          {
              'num_format':'0',
              'font_color': font_color,
              'bg_color': background_color,
              'border': 1
          }
      )  
  
  column_formats = { 
                      'A': ['Ticker', string_format],
                      'B': ['Price', dollar_format],
                      'C': ['Market Capitalization', dollar_format],
                      'D': ['Number of Shares to Buy', integer_format]
                      }

  for column in column_formats.keys():
      writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
      writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)  
      
  writer.save()
    
    
get_appl_info()
init_dataframe()
# update_dataframe()
batch_api_update_dataframe()  
calculate_shares_to_buy()
output_new_data()