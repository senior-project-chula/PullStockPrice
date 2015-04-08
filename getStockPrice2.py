# -*- coding: utf-8 -*-
'''
Created on March 31, 2015

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
# logname = 'D:/LUNAworkspace2/PullStockPrice/src/log/log_%s.log' %(datetime.now().strftime('%Y-%m-%d_%H:%M'))

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',filename=logname,level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

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

def save_price(stock_id=1,stock_helper=None,date_save=None,openprice=None,closeprice=None):
    latest_date = get_last_date(stock_id, stock_helper)
    if(date_save.date()<=latest_date.date()):
        logging.info("stock:%s price is already up to date",stock_id)
        return
    db = stock_helper.get_db()
    logging.info("Saving stock price for stock id = %s on date = %s",stock_id,date_save.strftime("%d/%m/%y"))
    cursor = db.cursor()
    logging.info("stock_id: %s openprice: %s closeprice: %s",stock_id,openprice,closeprice  )
    sql = ("insert into `SENIOR1`.`price` ( `Stock_ID`, `Opening_Price`, `Closing_Price`, `Date`) values ( %s, %s, %s, %s)")
    data = (stock_id,openprice,closeprice,cdate)
    cursor.execute(sql,data)
    logging.debug("RUN SQL:%s",cursor._executed)
    db.commit()
    db.close()

def get_stock_id(stock_name=None,stock_helper=None):
    if stock_helper==None:
        logging.error("there is something wrong with stock_helper")
        logging.error("trying to retrieve stock_id on stock name = %s",stock_name)
        return None
    db = stock_helper.get_db()
    cursor = db.cursor()
    sql = ("SELECT `Stock_ID` FROM `stock` WHERE `Stock_Name` = UPPER(%s)")
    data = (stockname,)
    cursor.execute(sql,data)
    logging.debug("RUN SQL:%s",cursor._executed)
    stock_id=str(cursor.fetchone()[0])
    db.commit()
    db.close()
    return stock_id

now_date=str(datetime.now().date())
logging.info("Current Date: %s", now_date)

# logging.info("Initializing Chrome")
# stock_helper = StockHelper('chrome')
logging.info("Initializing Firefox")
stock_helper = StockHelper('firefox')
driver = stock_helper.driver
driver.implicitly_wait(10)

link = r"http://www.settrade.com/C13_MarketSummary.jsp?detail=SET100"
driver.get(link)
driver.implicitly_wait(20)

# get the date
date_div = driver.find_elements_by_xpath("//div[@class='divDetailBox']//div[@class='gray96 txt10']")[0].get_attribute("innerHTML").strip()
date_list = date_div.split(' ')[1:3]
date_string = date_list[0].encode("utf-8") + " " + date_list[1].encode("utf-8")
logging.info("Latest update data on SetTrade is at %s", date_string)
cdate = datetime.strptime(date_string, "%d/%m/%Y %H:%M:%S")


logging.info("Finding set index")
table1s = driver.find_elements_by_xpath("//div[@class='divDetailBox']//div[@class='tablecolor1']")
table1sdivs=table1s[0].find_elements_by_tag_name("div")
closeprice=str(table1sdivs[1].get_attribute("innerHTML").strip())
closeprice = closeprice.replace(",","")
# print closeprice
logging.info("closeprice: %s",closeprice)

save_price('102', stock_helper, cdate, 0, closeprice)

logging.info("Finding set100 index")
table1sdivs=table1s[1].find_elements_by_tag_name("div")
closeprice= str(table1sdivs[1].get_attribute("innerHTML").strip())
closeprice = closeprice.replace(",","")
# print closeprice
logging.info("closeprice: %s",closeprice)

save_price('101', stock_helper, cdate, 0, closeprice)

link = r"http://www.settrade.com/C13_MarketSummarySET.jsp?command=SET100"
driver.get(link)
driver.implicitly_wait(20)
logging.info("Finding stock price")
table1s = driver.find_elements_by_xpath("//div[@class='divDetailBox']//div[@class='tablecolor1']")
table2s = driver.find_elements_by_xpath("//div[@class='divDetailBox']//div[@class='tablecolor2']")

tables = table1s+table2s


for t in tables:
    table1sdivs=t.find_elements_by_tag_name("div")
    stockname=str(table1sdivs[0].find_element_by_tag_name("a").get_attribute("innerHTML").strip())
#     print stockname
    openprice=str(table1sdivs[1].get_attribute("innerHTML").strip())
    openprice = openprice.replace(",","")
#     print openprice
    closeprice=str(table1sdivs[4].get_attribute("innerHTML").strip())
    closeprice = closeprice.replace(",","")
#     print closeprice
    logging.info("saving the price for stock=%s on date=%s",stockname,cdate.strftime("%d/%m/%y"))
    stock_id = get_stock_id(stockname, stock_helper)
    save_price(stock_id, stock_helper, cdate, openprice, closeprice)
#     print stock_id
    

driver.quit()
logging.info("DONE updating stock price for today")