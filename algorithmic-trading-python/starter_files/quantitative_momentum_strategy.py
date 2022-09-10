import my_util

import numpy as np #The Numpy numerical computing library
import pandas as pd #The Pandas data science library
import requests #The requests library for HTTP requests in Python
import xlsxwriter #The XlsxWriter libarary for 
import math #The Python math module
from scipy import stats #The SciPy stats module
from my_secrets import IEX_CLOUD_API_TOKEN


stocks = pd.read_csv('sp_500_stocks.csv')
my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']   
final_dataframe = pd.DataFrame(columns = my_columns)
symbol_groups = []
symbol_strings = [] 


def check_if_this_stock_has_significant_momentum():
  symbol = 'AAPL'
  api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}'
  data = requests.get(api_url).json()
  print(data['year1ChangePercent'])
  


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]   
        
def chunk_out_stocks():       
  global stocks 
  global symbol_groups
  global symbol_strings
  symbol_groups = list(chunks(stocks['Ticker'], 100))
  for i in range(0, len(symbol_groups)):
      symbol_strings.append(','.join(symbol_groups[i]))
  #     print(symbol_strings[i])

  
def make_batch_api_calls_and_store_each_stocks_momentum():
  global final_dataframe
  for symbol_string in symbol_strings:
  #     print(symbol_strings)
      batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
      data = requests.get(batch_api_call_url).json()
      for symbol in symbol_string.split(','):
          try:
            final_dataframe = final_dataframe.append(
              pd.Series([symbol, 
                        data[symbol]['quote']['latestPrice'],
                        data[symbol]['stats']['year1ChangePercent'],
                        'N/A'
                        ], 
                        index = my_columns), 
              ignore_index = True)
          except: 
            None
  print(final_dataframe)  
  
def remove_stocks_that_fall_below_momentum_threshold():
  global final_dataframe
  final_dataframe.sort_values('One-Year Price Return', ascending = False, inplace = True)
  final_dataframe = final_dataframe[:51]
  final_dataframe.reset_index(drop = True, inplace = True)
  print(final_dataframe)
  
def calc_shares_to_buy():
    global portfolio_size
    global hqm_dataframe
    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        calc_shares_to_buy()
        
    position_size = float(portfolio_size) / len(hqm_dataframe.index)
    for i in range(0, len(final_dataframe['Ticker'])):
        final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe['Price'][i])
    print(hqm_dataframe)
       
def init_high_quality_momentum_logic():
  global hqm_columns
  hqm_columns = [
                  'Ticker', 
                  'Price', 
                  'Number of Shares to Buy', 
                  'One-Year Price Return', 
                  'One-Year Return Percentile',
                  'Six-Month Price Return',
                  'Six-Month Return Percentile',
                  'Three-Month Price Return',
                  'Three-Month Return Percentile',
                  'One-Month Price Return',
                  'One-Month Return Percentile',
                  'HQM Score'
  ]
  global hqm_dataframe
  hqm_dataframe = pd.DataFrame(columns = hqm_columns)


def batch_api_call_hqm_logic():
    global symbol_strings
    global hqm_dataframe
    for symbol_string in symbol_strings:
      batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
      data = requests.get(batch_api_call_url).json()
      for symbol in symbol_string.split(','):
          try:
            hqm_dataframe = hqm_dataframe.append(
                                            pd.Series([symbol, 
                                                      data[symbol]['quote']['latestPrice'],
                                                      'N/A',
                                                      data[symbol]['stats']['year1ChangePercent'],
                                                      'N/A',
                                                      data[symbol]['stats']['month6ChangePercent'],
                                                      'N/A',
                                                      data[symbol]['stats']['month3ChangePercent'],
                                                      'N/A',
                                                      data[symbol]['stats']['month1ChangePercent'],
                                                      'N/A',
                                                      'N/A'
                                                      ], 
                                                      index = hqm_columns), 
                                            ignore_index = True)
          except:
            None

def calc_momentum_percentiles():
  global hqm_dataframe
  time_periods = [
                  'One-Year',
                  'Six-Month',
                  'Three-Month',
                  'One-Month'
                  ]

  for row in hqm_dataframe.index:
      for time_period in time_periods:
          try: 
            hqm_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'], hqm_dataframe.loc[row, f'{time_period} Price Return'])/100
          except:
            None
  # Print each percentile score to make sure it was calculated properly
  # for time_period in time_periods:
  #     print(hqm_dataframe[f'{time_period} Return Percentile'])

  #Print the entire DataFrame    
  print(hqm_dataframe)  
  

def select_50_best_stocks():
  global hqm_dataframe
  hqm_dataframe.sort_values(by = 'HQM Score', ascending = False)
  hqm_dataframe = hqm_dataframe[:51]
  calc_shares_to_buy()
  
def init_excel_writer():  
  global writer, string_template, dollar_template, integer_template, percent_template
  writer = pd.ExcelWriter('momentum_strategy.xlsx', engine='xlsxwriter')
  hqm_dataframe.to_excel(writer, sheet_name='Momentum Strategy', index = False)
  background_color = '#0a0a23'
  font_color = '#ffffff'

  string_template = writer.book.add_format(
          {
              'font_color': font_color,
              'bg_color': background_color,
              'border': 1
          }
      )

  dollar_template = writer.book.add_format(
          {
              'num_format':'$0.00',
              'font_color': font_color,
              'bg_color': background_color,
              'border': 1
          }
      )

  integer_template = writer.book.add_format(
          {
              'num_format':'0',
              'font_color': font_color,
              'bg_color': background_color,
              'border': 1
          }
      )

  percent_template = writer.book.add_format(
          {
              'num_format':'0.0%',
              'font_color': font_color,
              'bg_color': background_color,
              'border': 1
          }
      )  
  
def write_data_to_excel():
  global writer, string_template, dollar_template, integer_template, percent_template
  column_formats = { 
                      'A': ['Ticker', string_template],
                      'B': ['Price', dollar_template],
                      'C': ['Number of Shares to Buy', integer_template],
                      'D': ['One-Year Price Return', percent_template],
                      'E': ['One-Year Return Percentile', percent_template],
                      'F': ['Six-Month Price Return', percent_template],
                      'G': ['Six-Month Return Percentile', percent_template],
                      'H': ['Three-Month Price Return', percent_template],
                      'I': ['Three-Month Return Percentile', percent_template],
                      'J': ['One-Month Price Return', percent_template],
                      'K': ['One-Month Return Percentile', percent_template],
                      'L': ['HQM Score', integer_template]
                      }

  for column in column_formats.keys():
      writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 20, column_formats[column][1])
      writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], string_template)  
      
  writer.save()
            

  
def gather_monentum():
  chunk_out_stocks()
  make_batch_api_calls_and_store_each_stocks_momentum()
  calc_shares_to_buy()    
  
def hqm_logic():
  chunk_out_stocks()
  init_high_quality_momentum_logic()
  batch_api_call_hqm_logic()  
  calc_momentum_percentiles()
  select_50_best_stocks()
  init_excel_writer()
  write_data_to_excel()
    
  
if __name__ == "__main__":

  
  hqm_logic()
