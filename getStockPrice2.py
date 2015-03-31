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
# logname = '/home/seleuser/log/log_%s.log' %(datetime.now().strftime('%Y-%m-%d_%H:%M'))
logname = 'D:/LUNAworkspace2/PullStockPrice/src/log/log_%s.log' %(datetime.now().strftime('%Y-%m-%d_%H:%M'))

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',filename=logname,level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)


cdate=str(datetime.now().date())
logging.info("Current Date: %s", cdate)

# logging.info("Initializing Chrome")
# stock_helper = StockHelper('chrome')
logging.info("Initializing Firefox")
stock_helper = StockHelper('firefox')
driver = stock_helper.driver
driver.implicitly_wait(10)
db = stock_helper.get_db()
cursor = db.cursor()
link = r"http://www.settrade.com/C13_MarketSummary.jsp?detail=SET100"
driver.get(link)
driver.implicitly_wait(20)
logging.info("Finding set index")
table1s = driver.find_elements_by_xpath("//div[@class='divDetailBox']//div[@class='tablecolor1']")
table1sdivs=table1s[0].find_elements_by_tag_name("div")
closeprice=str(table1sdivs[1].get_attribute("innerHTML").strip())
closeprice = closeprice.replace(",","")
print closeprice
logging.debug("closeprice: %s",closeprice)
sql = ("insert into `SENIOR1`.`price` ( `Stock_ID`, `Opening_Price`, `Closing_Price`, `Date`) values ( '102', '0.0', %s, %s)")
data = (closeprice,cdate)
cursor.execute(sql,data)
print cursor._executed
logging.debug("RUN SQL:%s",cursor._executed)
logging.info("Finding set100 index")
table1sdivs=table1s[1].find_elements_by_tag_name("div")
closeprice= str(table1sdivs[1].get_attribute("innerHTML").strip())
closeprice = closeprice.replace(",","")
print closeprice
logging.debug("closeprice: %s",closeprice)
sql = ("insert into `SENIOR1`.`price` ( `Stock_ID`, `Opening_Price`, `Closing_Price`, `Date`) values ( '101', '0.0', %s, %s)")
data = (closeprice,cdate)
cursor.execute(sql,data)
print cursor._executed
logging.debug("RUN SQL:%s",cursor._executed)

link = r"http://www.settrade.com/C13_MarketSummarySET.jsp?command=SET100"
driver.get(link)
driver.implicitly_wait(20)
logging.info("Finding stock price")
table1s = driver.find_elements_by_xpath("//div[@class='divDetailBox']//div[@class='tablecolor1']")
table2s = driver.find_elements_by_xpath("//div[@class='divDetailBox']//div[@class='tablecolor2']")
i=0
while(i<50):
    print i
    table1sdivs=table1s[i].find_elements_by_tag_name("div")
    stockname=str(table1sdivs[0].find_element_by_tag_name("a").get_attribute("innerHTML").strip())
    print stockname
    openprice=str(table1sdivs[1].get_attribute("innerHTML").strip())
    openprice = openprice.replace(",","")
    print openprice
    closeprice=str(table1sdivs[4].get_attribute("innerHTML").strip())
    closeprice = closeprice.replace(",","")
    print closeprice
    sql = ("SELECT `Stock_ID` FROM `stock` WHERE `Stock_Name` = UPPER(%s)")
    data = (stockname,)
    cursor.execute(sql,data)
    logging.debug("RUN SQL:%s",cursor._executed)
    stock_id=str(cursor.fetchone()[0])
    print stock_id
    logging.debug("stock_id: %s",stock_id)
    logging.debug("openprice: %s",openprice)
    logging.debug("closeprice: %s",closeprice)
    sql = ("insert into `SENIOR1`.`price` ( `Stock_ID`, `Opening_Price`, `Closing_Price`, `Date`) values ( %s, %s, %s, %s)")
    data = (stock_id,openprice,closeprice,cdate)
    cursor.execute(sql,data)
    logging.debug("RUN SQL:%s",cursor._executed)
 
    table2sdivs=table2s[i].find_elements_by_tag_name("div")
    stockname=str(table2sdivs[0].find_element_by_tag_name("a").get_attribute("innerHTML").strip())
    print stockname
    openprice=str(table2sdivs[1].get_attribute("innerHTML").strip())
    openprice = openprice.replace(",","")
    print openprice
    closeprice=str(table2sdivs[4].get_attribute("innerHTML").strip())
    closeprice = closeprice.replace(",","")
    print closeprice
    sql = ("SELECT `Stock_ID` FROM `stock` WHERE `Stock_Name` = UPPER(%s)")
    data = (stockname,)
    cursor.execute(sql,data)
    logging.debug("RUN SQL:%s",cursor._executed)
    stock_id=str(cursor.fetchone()[0])
    print stock_id
    logging.debug("stock_id: %s",stock_id)
    logging.debug("openprice: %s",openprice)
    logging.debug("closeprice: %s",closeprice)
    sql = ("insert into `SENIOR1`.`price` ( `Stock_ID`, `Opening_Price`, `Closing_Price`, `Date`) values ( %s, %s, %s, %s)")
    data = (stock_id,openprice,closeprice,cdate)
    cursor.execute(sql,data)
    logging.debug("RUN SQL:%s",cursor._executed)
    i=i+1
db.commit()
db.close()
driver.quit()
logging.info("DONE updating stock price for today")