import boto3  
import configparser
import os
import sys
import json
import datetime
from dateutil.relativedelta import *


def getItems(client, grain, sDate, eDate, pToken):
    if pToken == '':
        return client.get_cost_and_usage( TimePeriod={'Start':sDate, 'End': eDate}, Granularity=grain, Metrics=['UnblendedCost','UsageQuantity'], GroupBy=[{'Type':'DIMENSION','Key':'SERVICE'}])
    else:
        return client.get_cost_and_usage( TimePeriod={'Start':sDate, 'End': eDate}, Granularity=grain, Metrics=['UnblendedCost','UsageQuantity'], GroupBy=[{'Type':'DIMENSION','Key':'SERVICE'}], NextPageToken=pToken)

def doStuff(session,account):

    try:
        alias = session.client('iam').list_account_aliases()['AccountAliases'][0]
    except:
        alias = account

    client = session.client("ce")

    dayList = []
    monList = []

    sDate = datetime.datetime.now() - datetime.timedelta(days=365)
    eDate = datetime.datetime.now() + datetime.timedelta(days=1)
    ddelta = datetime.timedelta(days=1)
    mdelta = relativedelta(months=1)

    dayData = {}
    tmp = sDate
    while tmp <= eDate:
        dayData[tmp.strftime("%d-%b-%Y")] = {}
        dayList.append(tmp.strftime("%d-%b-%Y"))
        tmp += ddelta

    token = ""
    dayCost = {}
    dayUsage = {}
    while(True):
        items = getItems(client, "DAILY", sDate.strftime("%Y-%m-%d"), eDate.strftime("%Y-%m-%d"), token)
        for item in items["ResultsByTime"]:
            for group in item["Groups"]:
                thisGrp = group["Keys"][0].replace("AWS ","").replace("Amazon ","").replace("AmazonCloudWatch","CloudWatch")

                thisDay = datetime.datetime.strptime(item["TimePeriod"]["Start"], "%Y-%m-%d")
                strDate = thisDay.strftime("%d-%b-%Y")
                dayData[strDate][thisGrp] = {
                    "cost": float(group["Metrics"]["UnblendedCost"]["Amount"]),
                    "usage": float(group["Metrics"]["UsageQuantity"]["Amount"])
                }
                if thisGrp not in dayCost:
                    dayCost[thisGrp] = 0
                if thisGrp not in dayUsage:
                    dayUsage[thisGrp] = 0

                dayCost[thisGrp] += float(group["Metrics"]["UnblendedCost"]["Amount"])
                dayUsage[thisGrp] += float(group["Metrics"]["UsageQuantity"]["Amount"])
                    
        try:
            token = items["NextPageToken"]
        except:
            break

    sortDayCost = sorted(dayCost.items(), key=lambda x: x[1], reverse=True)
    sortDayUsage = sorted(dayUsage.items(), key=lambda x: x[1], reverse=True)

    monData = {}
    tmp = sDate
    while tmp <= eDate:
        monData[tmp.strftime("%b-%Y")] = {}
        monList.append(tmp.strftime("%b-%Y"))
        tmp += mdelta

    token = ""
    monCost = {}
    monUsage = {}
    while(True):
        items = getItems(client, "MONTHLY", sDate.strftime("%Y-%m-%d"), eDate.strftime("%Y-%m-%d"), token)
        for item in items["ResultsByTime"]:
            for group in item["Groups"]:
                thisGrp = group["Keys"][0].replace("AWS ","").replace("Amazon ","").replace("AmazonCloudWatch","CloudWatch")
                
                thisDay = datetime.datetime.strptime(item["TimePeriod"]["Start"], "%Y-%m-%d")
                strDate = thisDay.strftime("%b-%Y")
                monData[strDate][thisGrp] = {
                    "cost": float(group["Metrics"]["UnblendedCost"]["Amount"]),
                    "usage": float(group["Metrics"]["UsageQuantity"]["Amount"])
                }   
                if thisGrp not in monCost:
                    monCost[thisGrp] = 0
                if thisGrp not in monUsage:
                    monUsage[thisGrp] = 0

                monCost[thisGrp] += float(group["Metrics"]["UnblendedCost"]["Amount"])
                monUsage[thisGrp] += float(group["Metrics"]["UsageQuantity"]["Amount"])


        try:
            token = items["NextPageToken"]
        except:
            break

    sortMonCost = sorted(monCost.items(), key=lambda x: x[1], reverse=True)
    sortMonUsage = sorted(monUsage.items(), key=lambda x: x[1], reverse=True)

    ### DAILY COSTS
    outF = open("DAILY-COST-" + alias + ".csv", "w")
    line = "Date"
    for i, j in sortDayCost:
        line += "," + i
    outF.write(line + "\n")
    for d in dayList:
        line = d
        for i, j in sortDayCost:
            try:
                line = line + "," + str(round(dayData[d][i]["cost"], 4))
            except:
                line = line + ",0.0"
        outF.write(line + "\n")
    outF.close()    

    ### DAILY USAGE
    outF = open("DAILY-USAGE-" + alias + ".csv", "w")
    line = "Date"
    for i, j in sortDayUsage:
        line += "," + i
    outF.write(line + "\n")
    for d in dayList:
        line = d
        for i, j in sortDayUsage:
            try:
                line = line + "," + str(round(dayData[d][i]["usage"], 4))
            except:
                line = line + ",0.0"
        outF.write(line + "\n")
    outF.close()    

    ### MONTHLY COSTS
    outF = open("MONTHLY-COST-" + alias + ".csv", "w")
    line = "Date"
    for i, j in sortMonCost:
        line += "," + i
    outF.write(line + "\n")
    for d in monList:
        line = d
        for i, j in sortMonCost:
            try:
                line = line + "," + str(round(monData[d][i]["cost"], 4))
            except:
                line = line + ",0.0"
        outF.write(line + "\n")
    outF.close()    

    ### MONTHLY USAGE
    outF = open("MONTHLY-USAGE-" + alias + ".csv", "w")
    line = "Date"
    for i, j in sortMonUsage:
        line += "," + i
    outF.write(line + "\n")
    for d in monList:
        line = d
        for i, j in sortMonUsage:
            try:
                line = line + "," + str(round(monData[d][i]["usage"], 4))
            except:
                line = line + ",0.0"
        outF.write(line + "\n")
    outF.close()    

        
def main():
    try:
        cnt = len(sys.argv) - 1
        if cnt == 1:
            account = sys.argv[1].lower().strip()
            print("\nAlias:" + account + "\n")
            session = boto3.Session(profile_name=account)
            doStuff(session,account)
        else:
            config = configparser.ConfigParser()
            confFile = os.path.expanduser('~/.aws/config')
            config.read(confFile)

            profiles = config.sections()
            aliases = []
            for profile in profiles:
                aliases.append(profile.replace("profile ",""))
            aliases.sort()

            for account in aliases:
                print("\nAlias:" + account + "\n")
                session = boto3.Session(profile_name=account)
                doStuff(session,account)
    except:
        print("error")

if __name__ == '__main__':
    main()
