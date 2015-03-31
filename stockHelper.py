'''
Created on 12 Feb 2558

@author: Putt
'''
import os
import time

from selenium import webdriver
import selenium

import MySQLdb

class StockHelper(object):
    '''
    classdocs
    this is to set up the stock web driver
    '''
#     savepath = "D:\\stockanalysis\\"+time.strftime("%d%m%y")+"\\"
    savepath = '/home/senior/stockanalysis/%s/' %(time.strftime("%d%m%y"))
#     savepath = '/Users/potsaweevechpanich/Developer/senior/stockanalysis/%s/' %(time.strftime("%d%m%y"))
#     chrome_path = r'C:\Python27\Scripts\chromedriver.exe'
    chrome_path = r'/usr/local/bin/chromedriver'
#     folderpath = '/home/senior/stockanalysls'
#     subfolderpath='/&s/' %(time.strftime("%d%m%y"))
    
#     folderpath = 'D:\\stockanalysis\\'
#     subfolderpath='&s' %(time.strftime("%d%m%y"))
    
#     host = "127.0.0.1"
    host = "docker"
    db_user = "root"
    db_password = "password"
    schema = "SENIOR1"
    driver=None
    browser = 'firefox'
    
    def __init__(self, browser='firefox'):
        '''
        Constructor
        '''
        self.browser = browser
        
#         try:
#             os.stat(self.savepath)
#         except:
#             os.mkdir(self.savepath)
        self.driver = self.create_driver()
        
        
    def get_db(self):
        return MySQLdb.connect(self.host,self.db_user,self.db_password,self.schema)
    
    def create_driver(self):
        if self.browser == 'firefox':
            profile = webdriver.FirefoxProfile()
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.manager.showWhenStarting", False)
            profile.set_preference("browser.download.dir", self.savepath)
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            profile.set_preference("pdfjs.disabled", True)
            profile.set_preference("plugin.scan.Acrobat", "99.0")
            profile.set_preference("plugin.scan.plid.all", False)
            
            return webdriver.Firefox(firefox_profile=profile)
            
            

        elif self.browser=='chrome':
            chromeOptions = webdriver.ChromeOptions()
            prefs = {"download.default_directory" : self.savepath,
                     "plugins.plugins_disabled": ["Chrome PDF Viewer"]}
            chromeOptions.add_experimental_option("prefs",prefs)
            return webdriver.Chrome(executable_path=self.chrome_path, chrome_options=chromeOptions)
    
