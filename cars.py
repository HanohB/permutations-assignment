import pandas as pd
import requests
import numpy as np
import json
from datetime import date, datetime
import os, sys
import itertools

def get_val_from_json(col):
    years = []
    for i in col:
        years.append(i["year"])
    return years
def time_delta(year):
    d0 = date(year, 1, 1)
    d1 = date.today()
    return (d1-d0).days
def USD_to_CLP(URL):
    response = requests.get(URL)
    response = response.json()
    return response["data"]['rates']['CLP']
def expand_grid(itrs):
   product = list(itertools.product(*itrs))
   return {'Var{}'.format(i+1):[x[i] for x in product] for i in range(len(itrs))}
def col_to_list(possibleVals):
    return possibleVals.split(";")
def possible_val_converter(posVals):
    convertedList = []
    for val in posVals:
        try:
            convertedList.append(int(val))
        except ValueError:
            try:
                convertedList.append(float(val))
            except ValueError:
                try:
                    convertedList.append(json.loads(val))
                except:
                    if val == 'True' or val == 'False' or val =='TRUE' or val == 'FALSE':
                        convertedList.append(val == 'True')
                    else:
                        convertedList.append(val)
    return convertedList
##Reading excel as pandas dataframe.
def main(argv):
    ##argv[1]: cars.xlsx file
    CarsData_path = argv[1]
    cars_dataframe = pd.read_excel(CarsData_path, index_col = 0, header = 0)
    ##Parsing possible values and transposing the dataframe to match the needed convention.
    cars_dataframe["Possible Values"] = cars_dataframe["Possible Values"].apply(col_to_list)
    cars_dataframe = cars_dataframe.T
    ##Iterate over every possible values cell and convert each value to it's expected type (str, bool, int, float, etc)
    possible_val_list = []
    for col in cars_dataframe.columns:
        possible_val_list.append(possible_val_converter(cars_dataframe[col].tolist()[0]))
    ##On the converted possible values, call expand_grid which permutates all of the possible dataframes.
    permutation_dataframe = pd.DataFrame(expand_grid(possible_val_list))
    ##Change permutation dataframe headers to cars_dataframe headers.
    permutation_dataframe.columns = cars_dataframe.columns
    permutation_dataframe['Q3-EngineSize'] = np.where(permutation_dataframe['Q1-IsElectric'] == 'True', None, permutation_dataframe['Q3-EngineSize'])
    ##Building the function
    #1:Fill col with year, 2: Fill col with time delta based on the year, 3: Multiply by Q2-KM, 4: Multiple by USD to CLP exchange rate.
    permutation_dataframe["Price"] = get_val_from_json(permutation_dataframe["Q5-ModelData"])
    permutation_dataframe["Price"] = permutation_dataframe["Price"].apply(time_delta)
    permutation_dataframe["Price"] = permutation_dataframe["Price"] * permutation_dataframe["Q2-KM"] 
    permutation_dataframe["Price"] = permutation_dataframe["Price"].multiply(float(USD_to_CLP("https://api.coinbase.com/v2/exchange-rates?currency=USD")))
    ##Write permutation dataframe in a new excel file.
    permutation_dataframe.to_excel("Permutations " + str(date.today()) + ".xlsx")

if __name__ == "__main__":
    #Only call main() when this file is run directly, ignore if imported
    main(sys.argv)


