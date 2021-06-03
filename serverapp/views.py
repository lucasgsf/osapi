from django.shortcuts import render

from django.shortcuts import render
import numpy as np
import pandas as pd
import uuid
from pandas_datareader import data
import matplotlib.pyplot as plt

# Create your views here.
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import requests

from .models import *
from .serializers import *

class CalculoAcaoView(APIView):
    def get(self, request, *args, **kwargs):

      # acao = data=request.data

      return Response("OK", status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        calculo_serializer = CalculoAcaoSerializer(data=request.data)

        if calculo_serializer.is_valid():
          lstAcoes = []

          for acao in calculo_serializer.data['lstAcoes']:
            lstAcoes.append(acao['nome'])

          # Import data
          # df = data.DataReader(['AAPL', 'NKE', 'GOOGL', 'AMZN'], 'yahoo', start='2015/01/01', end='2019/12/31')
          df = data.DataReader(lstAcoes, 'yahoo', start=calculo_serializer.data['dtInicio'], end=calculo_serializer.data['dtFim'])

          # Closing price
          df = df['Adj Close']

          # --- MATRIZ DE COVARIANCIA E CORRELACAO

          # Log of percentage change
          cov_matrix = df.pct_change().apply(lambda x: np.log(1+x)).cov()

          corr_matrix = df.pct_change().apply(lambda x: np.log(1+x)).corr()

          # --- VARIANCIA DO PORTIFOLIO --- IMAGEM DO SLIDE !!!!!!!!!!!!!

          # Randomly weighted portfolio's variance
          # w = {'MSFT': 0.2, 'NVDA': 0.2, 'PYPL': 0.2, 'NFLX': 0.2, 'CMCSA': 0.2}
          # port_var = cov_matrix.mul(w, axis=0).mul(w, axis=1).sum().sum()

          # --- RETORNO ESPERADO DO PORTIFOLIO ---
          
          # Yearly returns for individual companies
          ind_er = df.resample('Y').last().pct_change().mean()

          # --- FRONTEIRA EFICIENTE ---

          # Volatility is given by the annual standard deviation. We multiply by 250 because there are 250 trading days/year.
          ann_sd = df.pct_change().apply(lambda x: np.log(1+x)).std().apply(lambda x: x*np.sqrt(250))

          p_ret = [] # Define an empty array for portfolio returns
          p_vol = [] # Define an empty array for portfolio volatility
          p_weights = [] # Define an empty array for asset weights

          num_assets = len(df.columns)
          num_portfolios = 10000

          for portfolio in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights = weights/np.sum(weights)
            p_weights.append(weights)
            returns = np.dot(weights, ind_er) # Returns are the product of individual expected returns of asset and its 
                                              # weights 
            p_ret.append(returns)
            var = cov_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()# Portfolio Variance
            sd = np.sqrt(var) # Daily standard deviation
            ann_sd = sd*np.sqrt(250) # Annual standard deviation = volatility
            p_vol.append(ann_sd)
          
          data2 = {'Returns':p_ret, 'Volatility':p_vol}

          for counter, symbol in enumerate(df.columns.tolist()):
            data2[symbol+' weight'] = [w[counter] for w in p_weights]
          
          portfolios = pd.DataFrame(data2)

          min_vol_port = portfolios.iloc[portfolios['Volatility'].idxmin()]
          # idxmin() gives us the minimum value in the column specified.
          min_vol_port

          # Finding the optimal portfolio
          rf = (calculo_serializer.data['vlRisco'] / 100) # risk factor

          optimal_risky_port = portfolios.iloc[((portfolios['Returns']-rf)/portfolios['Volatility']).idxmax()]
          optimal_risky_port

          imgUrl = "resultados/"+str(uuid.uuid4().hex)+".png"

          # Plotting optimal portfolio
          plt.subplots(figsize=(10, 10))
          plt.scatter(portfolios['Volatility'], portfolios['Returns'],marker='o', s=10, alpha=0.3)
          plt.scatter(min_vol_port[1], min_vol_port[0], color='r', marker='*', s=500)
          plt.scatter(optimal_risky_port[1], optimal_risky_port[0], color='g', marker='*', s=500)
          plt.savefig(imgUrl)

          retorno = {
            "matrizCov": cov_matrix,
            "matrizCorr": corr_matrix,
            "imgUrl": imgUrl,
            "resultado": optimal_risky_port
          }

          return Response(retorno, status=status.HTTP_201_CREATED)
        else:
          return Response(calculo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)