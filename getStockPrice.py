# -*- coding: utf-8 -*-
'''
Created on Jan 11, 2015

@author: Ing
'''
import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException
import os
import os.path
import MySQLdb
from datetime import datetime
from stockHelper import StockHelper
import logging
from time import strptime

# logname = 'log/log_%s.log' %(datetime.now().strftime('%Y-%m-%d_%H:%M'))
logname = '/home/seleuser/log/log_%s.log' %(datetime.now().strftime('%Y-%m-%d_%H:%M'))

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',filename=logname,level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

def savePrice(driver,stock_name,stock_id,stock_helper,latest_date):
    logging.info("get the pirce of %s (id=%s) that is older than %s",stock_name,stock_id,latest_date.strftime("%d/%m/%y"))
    count=0;
    db = stock_helper.get_db()
    cursor = db.cursor()
    table1s = driver.find_elements_by_xpath("//div[@class='tablecolor1']")
    table2s = driver.find_elements_by_xpath("//div[@class='tablecolor2']")
    driver.implicitly_wait(20)
    tables=table1s+table2s
    for table1 in tables:
#         print(count)
        
        contents=table1.find_elements_by_tag_name("div")
        driver.implicitly_wait(20)
        datetemp=contents[0].get_attribute("innerHTML").strip()
        logging.info("Extracting date %s",datetemp)
        driver.implicitly_wait(20)
        this_row_date = datetime.strptime(datetemp,"%d/%m/%y")    
        if(this_row_date.date()<=latest_date.date()):
            logging.warning("This row is already added in the DB")
            continue    
        sql = ("INSERT INTO `price`(`Opening_Price`, `Closing_Price`, `Date`, `Stock_ID`) VALUES (%s,%s,%s,%s)")
        opening_price=contents[1].get_attribute("innerHTML").strip()
        highest_price=contents[2].get_attribute("innerHTML").strip()
        lowest_price=contents[3].get_attribute("innerHTML").strip()
        avg_price=contents[4].get_attribute("innerHTML").strip()
        closing_price=contents[5].get_attribute("innerHTML").strip()
        date_str=str(this_row_date)
        data=(opening_price,closing_price,date_str,stock_id)
        logging.info("save data of stock:%s date:%s open:%s close:%s",stock_name,date_str,opening_price,closing_price)
        cursor.execute(sql,data)
        logging.debug("RUN SQL:%s",cursor._executed)
        count=count+1
    db.commit()
    db.close()
    logging.info("Done updating price for %s (id=%s)",stock_name,stock_id)

def get_last_date(stock_id=1,stock_helper=None):
    if(stock_helper==None):
        return None
    db = stock_helper.get_db()
    logging.info("getting the latest date of this stock id = %s",stock_id)
    cursor = db.cursor()
    sql = ("SELECT MAX(`price`.`Date`) FROM `price` WHERE `price`.`Stock_ID`=%s")
    data=[stock_id]
    cursor.execute(sql,data)
    logging.debug("RUN SQL:%s",cursor._executed)
    latest_date=cursor.fetchone()[0]
    logging.info("get latest date = %s",latest_date)
    db.commit()
    db.close()
    return latest_date

logging.info("Initializing Firefox")
stock_helper = StockHelper('firefox')
driver = stock_helper.driver
driver.implicitly_wait(10)
db = stock_helper.get_db()
cursor = db.cursor()
logging.info("Getting SET100 Stock name and id list")
sql = ("SELECT `Stock_Name`,`Stock_ID` FROM `stock` WHERE Is_Index=0")
cursor.execute(sql)
stockNames=cursor.fetchall()
logging.debug("RUN SQL:%s",cursor._executed)
db.commit()
db.close()
for stockName in stockNames:
    logging.info("==============================")
    logging.info("Extracting stock name %s with ID=%s",stockName[0],stockName[1])
    link="http://www.settrade.com/C04_02_stock_historical_p1.jsp?txtSymbol="+stockName[0]+"&selectPage=2&max=10&offset=0"
    logging.info("Opening the link %s",link)
    driver.get(link)
    driver.implicitly_wait(20)
    latest_date = get_last_date(stockName[1], stock_helper)
#     logging.info("stock_Name = "+stockName[0])
#     logging.info("stock_id = "+str(stockName[1]))
    savePrice(driver,str(stockName[0]),str(stockName[1]),stock_helper,latest_date)

#Save Index
link = r"http://www.settrade.com/C13_FiveDays.jsp"
driver.get(link)
driver.implicitly_wait(20)
logging.info("Finding set index")
table2s = driver.find_elements_by_xpath("//td[@class='tablecolor2']")
date = table2s[0].get_attribute("innerHTML").strip()
set_index = table2s[1].get_attribute("innerHTML").strip()
set_100_index = table2s[3].get_attribute("innerHTML").strip()

# Extract date
date = date.replace("<strong>","")
date = date.replace("</strong>","")
date_list = date.split(" ")
month_array={"ม.ค.":"01","ก.พ.":"02","มี.ค.":"03","เม.ย.":"04","พ.ค.":"05","มิ.ย.":"06","ก.ค.":"07","ส.ค.":"08","ก.ย.":"09","ต.ค.":"10","พ.ย.":"11","ธ.ค.":"12"}
try:
    date_day = date_list[0].encode('utf-8')
    if len(date_day)==1:
        date_day = "0"+str(date_day)
    else:
        date_day = str(date_day)
    date_month = date_list[1].encode('utf-8')
    date_year = str(int(date_list[2])-43)
    date_month_num = month_array[date_month]
    tim = date_list[3].encode("utf-8")
#     print tim
    fulldate=date_day+"/"+date_month_num+"/"+date_year+" "+tim
    date = datetime.strptime(fulldate,"%d/%m/%y %H:%M:%S")
    logging.info("last date appear on setTrade is %s",fulldate)
except:
    logging.warning("Can not extract date from set trade! using today date right now instead")
    date=datetime.now()

latest_date = get_last_date(101, stock_helper)

if(latest_date<date):
    # cutting down tags
    set_index = set_index.split("<")[0]
    set_100_index = set_100_index.split("<")[0]
    
    set_index = set_index.replace(",","")
    set_100_index = set_100_index.replace(",","")
    
    logging.info("Today SET index = %s", set_index)
    logging.info("Today SET 100 index = %s", set_100_index)
    
    logging.info("Saving set index to database")
    db = stock_helper.get_db()
    cursor = db.cursor()
    sql = ("insert into `SENIOR1`.`price` ( `Stock_ID`, `Opening_Price`, `Closing_Price`, `Date`) values ( '101', '0', %s, %s)")
    data = (set_100_index,date)
    cursor.execute(sql,data)
    logging.debug("RUN SQL:%s",cursor._executed)
    
    sql = ("insert into `SENIOR1`.`price` ( `Stock_ID`, `Opening_Price`, `Closing_Price`, `Date`) values ( '102', '0', %s, %s)")
    data = (set_index,date)
    cursor.execute(sql,data)
    logging.debug("RUN SQL:%s",cursor._executed)
    
    db.commit()
    db.close()
else:
    logging.info("SET and SET100 index in the database is already up-to-date")

driver.quit()
logging.info("DONE updating stock price for today")