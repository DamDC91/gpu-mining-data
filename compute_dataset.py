#!/usr/bin/env python3

import csv
import json
import math
import copy
from datetime import datetime, date
from typing import List, Dict, Tuple


def get_electricity_price() -> List[Tuple[date, float]]:
    with open("./data-src/electricity_price.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        data = [(datetime.strptime(row["Month"], "%b %Y").date(), float(row["cents_per_kwh"])) for row in reader if row["cents_per_kwh"] != ""]
        return data

def same_month(a: date, b: date) -> bool:
    assert((all(isinstance(x, date) for x in (a, b))))
    return a.year == b.year and a.month == b.month

def get_bitcoin_data() -> Tuple[List[date], List[float], List[float]]:
    with open("./data-src/difficulty.json", "r") as jsonfile:
        data = json.load(jsonfile) 

        length = len(data["difficulty"])
        difficulty_average = 0
        market_price_average = 0
        count = 0
        current_month = None
        difficulty: List[float] = []
        market_price: List[float] = []
        _date: List[date] = []

        for i in range(0,length):
            current_date = datetime.fromtimestamp(data["difficulty"][i]["x"]/1000).date()

            if current_month == None:
                current_month = current_date

            if same_month(current_month, current_date):
                difficulty_average += data["difficulty"][i]["y"]
                market_price_average += data["market-price"][i]["y"]
                count += 1
                
            else:
                difficulty.append(difficulty_average/float(count))
                market_price.append(market_price_average/float(count))


                current_month = current_date
                current_month = current_month.replace(day = 1)
                count = 0
                difficulty_average = data["difficulty"][i]["y"]
                market_price_average = data["market-price"][i]["y"]
                _date.append(current_month)

        return (_date, difficulty, market_price)



def get_gpu_data() -> List[dict]:
    with open("./data-src/gpus.json", "r") as jsonfile:
        gpus_list = []

        data = json.load(jsonfile)
        desktop_gpu  = data["categories"][0]["generations"]
        for gen in desktop_gpu:
            for gpus in gen["gpus"]:
                tmp = {}
                keys = gpus.keys()
                if "model" in keys:
                    tmp["name"] = gpus["model"]
                if "tdp" in keys:
                    tmp["tdp"] = int(gpus["tdp"])
                    
                if "launch" in keys:
                    tmp["date"] = datetime.strptime(gpus["launch"], "%Y-%m-%d").date()
                
                if "processing_power" in keys:
                    tmp["hash_rate"] = float(gpus["processing_power"])

                if len(tmp.keys()) == 4:
                    tmp['net_worth'] = -math.inf
                    gpus_list.append(tmp)

    return gpus_list

def get_block_reward(date) -> float:
    return float(50 * 1/2 ** (math.floor((date.year - 2009) / 4.0)))

class DateTimeEncoder(json.JSONEncoder):
    """JSON serializer for objects not serializable by default json code"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return str(obj.isoformat())
        raise TypeError ("Type %s not serializable" % type(obj))

bitcoin_date, difficulty, market_price = get_bitcoin_data()
electricity_price = get_electricity_price()
gpus = get_gpu_data()
dataset: List[Dict[str, Dict]] = []

i = 0
for month in bitcoin_date:
    elec_price = [p for p in electricity_price if p[0] == month]
    if len(elec_price) > 0 and month >= date(2011,1,1):
        for gpu in gpus:
            if gpu["date"] <= month:
                number_of_gpus = 1e9
                time = (difficulty[i] / (number_of_gpus * gpu["hash_rate"])) / (60 * 60 * 24) # in days
                kwh = number_of_gpus * (gpu["tdp"] * 24 * time) / 1000.0
                cost = (kwh * elec_price[0][1] / 100.0) # cost in $
                reward = get_block_reward(month) * market_price[i]
                gpu["net_worth"]  = reward - cost

        gpus.sort(reverse=True, key=lambda x:x['net_worth'])
        best_gpus = {"month" : month.isoformat(), "gpus": [gpu.copy() for gpu in gpus[:5] if gpu["net_worth"] > 0]}

        if len(best_gpus["gpus"]) >= 5:
            dataset.append(best_gpus)
    i = i  + 1

print(json.dumps(dataset, cls=DateTimeEncoder, indent=4))
