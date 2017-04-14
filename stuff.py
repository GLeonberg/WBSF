import plotly.plotly as py
import plotly.figure_factory as go
import plotly.graph_objs as obj
import time
import pandas_datareader.data as web
import json
import LATest
import os
import os.path
from yahoo_finance import Share
from openpyxl import load_workbook # openpyxl is used for xlsx files, a.k.a excel files from 2010+, old excel files used xls
from datetime import datetime
from googlefinance import getQuotes
from plotly.graph_objs import *
import numpy as np



def makeLineGraph(stockSymbol,Webster,currentInfo): # Makes Line graph for both historic data (webster), current Stock Info (currentInfo)
	figure=obj.Scatter(y=Webster.High,x=Webster.index) # Line 
	currentFigure=obj.Trace(y=currentInfo[0]['LastTradePrice'],x=currentInfo[0]['LastTradeDateTime'],line=dict(color=('rgb(0,0,0)'))) # Current Point Data
	data=[figure,currentFigure]
	py.plot(data, filename=stockSymbol+'_Line')

def makeCandleStickGraph(stockSymbol,Webster): # Makes a Candle Stick Graph
	fig=go.create_candlestick(Webster.Open,Webster.High,Webster.Low,Webster.Close,dates=Webster.index) # Past Data
	py.plot(fig,filename=stockSymbol+'_Candle',validate=False)

def fetchData(stockSymbol,startYear,endYear): # Fecthes the data between any two year points
	info=web.DataReader(stockSymbol,'yahoo',datetime(int(startYear),1,1),datetime(int(endYear),1,1)) 
	return info

def fetchDataToday(stockSymbol,startYear): # Fethes  past data to today
	info=web.DataReader(stockSymbol,'yahoo',datetime(startYear,1,1),time.strftime("%d-%m-%Y"))
	return info

def fetchDataSpec(stockSymbol,month):
	info=web.DataReader(stockSymbol,'yahoo',datetime(int(time.strftime("%Y")),int(month),1),time.strftime("%d-%m-%Y"))
	return info

def fetchGoogData(stockSymbol): #Fetches current google data
	currentInfo=getQuotes(stockSymbol)
	return currentInfo

def totalTogether(stockSymbol,Webster,currentInfo,Predict,Pointy,sy): #plots all the graphs together
	#fig=go.create_candlestick(Webster.Open,Webster.High,Webster.Low,Webster.Close,dates=Webster.index)
	figure=obj.Trace(y=Webster.High,x=Webster.index,line=dict(color=('rgb(0,50,100)')),name="Past Data for "+stockSymbol)
	currentFigure=obj.Trace(y=currentInfo[0]['LastTradePrice'],x=currentInfo[0]['LastTradeDateTime'],line=dict(color=('rgb(0,0,0)')),name='Current Data for '+stockSymbol)
	Predicts=obj.Trace(y=Predict,x=getIndex(30,Webster.index),line=dict(color=('rgb(255,165,0)')),name="Prediction "+stockSymbol)
	point=obj.Trace(y=Pointy,x=currentInfo[0]['LastTradeDateTime'],line=dict(color=('rgb(255,165,0)')),name="Prediction "+stockSymbol)
	data=Data([figure,currentFigure,Predicts,point])
	py.plot(data, filename=stockSymbol+'_Line')


def getIndex(num,index):
	length=len(index)
	a=np.array(index[length-num])
	for x in range(length-num,length):
		a=np.append(a,index[x])
		pass
	return a

def get_companysymbol(var): # Looks up the current company 
	name = var
	wb = load_workbook('companylist.xlsx')		
	sheet_ranges = wb['Worksheet']      									# you need the name of the sheet which is in the bottom of the excel file once you open it
	end_range = 3196														# the total number of companies in the list are 3195
	true = 0
	num=0
	for num in range(1,3196):			
		company_name = sheet_ranges['B'+str(num)].value					
		if name.lower() in company_name.lower(): 							# convert user input and the cell entry to upper to avoid hassles when checking
			true = 1														# if you found the company, then it exists, hence true = 1
			break															# break the loop if you find the company you're looking for
	if true==0:
		print("Could not find the company symbol")							
		return "null"
	else:
		return sheet_ranges['A'+str(num)].value	
def main():
	var='' #just want update to repeat not entire thing 
	while var!='null':
		Time=datetime.now().strftime('%M')
		company_name=input("Enter the name of the company you're searching for ") 
		var = get_companysymbol(company_name)	
		if var != 'null':								
			timeBegin=int(input('Enter Start year ')) - 2
			totalDataCurrent=fetchDataToday(var,timeBegin)
			googData=fetchGoogData(var)
			Prediction_Data=fetchDataSpec('AAPL',int(time.strftime("%m"))-1)
			Prediction_Data_Length=len(Prediction_Data.High)
			Coeffcients=LATest.coeffcients_Generator(LATest.makeXVals_Matrix(10,timeBegin,Prediction_Data_Length),LATest.makeY_Matrix(Prediction_Data.High))
			Prediction_Model=LATest.makeOutY(Coeffcients,Prediction_Data_Length+3,timeBegin,totalDataCurrent.High,googData)
			pointY=LATest.getPointY(Coeffcients,timeBegin,totalDataCurrent.High[len(totalDataCurrent.High)-1])
			totalTogether(var,totalDataCurrent,googData,Prediction_Model,pointY,timeBegin)
	pass
main() 
#C:\\cygwin\bin\stuff.py
