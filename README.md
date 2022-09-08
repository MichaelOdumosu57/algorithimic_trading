# Algorithmic Trading w/ Python

## Algorithmic Trading Basis
* using computers to make investment decisions
* Renaissance Techologies: best performing in the space
* use numpy, underlying code in C


### Trading Process
* collect data
* develop a hypothesis
* backtest the strategy
* implement step in production


* in project build an alternative s&p 500 where every company holds same weight,apple wont be big best buy wont be small
* value investing
  * hope you can buy for a dollar to 75c and go up to a dollar later


* imported lbs
```py
import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math

```

* import 500 stocks from s&p 500

```py
csv = "{}\\{}".format(os.getcwd(),"sp_500_stocks.csv")
stocks = pd.read_csv(csv)
print(stocks)
```

* acquier IEX cloud API
* panda series is like a python a list
* panda Datafromae is a 2d list