# Install chromedriver for selenium to work
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
import chromedriver_autoinstaller
import pandas as pd
from time import sleep 
import datetime as dt
import random

# creating a chrome instance 
def invoke_chrome_instance():
    driver_path = chromedriver_autoinstaller.install()
    options = Options()
    options.headless = False
    options.add_argument('--disable-gpu')
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(executable_path = driver_path,options = options)
    driver.set_page_load_timeout(100)
    
    return driver


# function to login to twitter
def login_twitter(username,password,driver):
    try: 
        sleep(random.uniform(1,5))
        driver.get("https://twitter.com/login")
        xpath_username = '//input[@name="session[username_or_email]"]'
        path_username = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, xpath_username)))
        path_username.send_keys(username)
        xpath_password = '//input[@name="session[password]"]'
        path_password = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, xpath_password)))
        path_password.send_keys(password)
        
        path_password.send_keys(Keys.RETURN)
    
    except:
        print("Unable to login twitter")
        return False

# function to search
def advance_search(driver,lang=None,sent_from = None, sent_to =None, mention= None,start_date= None, end_date = None):
  
    
    # set language
    if lang:
        lang = "lang%3A"+lang+"%20"
    else:
        lang =""
        
    # set from account
    if sent_from:
        sent_from = "(from%3A"+sent_from+")%20"
    else:
        sent_from = ""
            
     # set to account       
    if sent_to:
        sent_to = "(to%3A"+sent_to+")%20"
    else:
        sent_to = ""
    
    # set mention account
    if mention:
        mention = "(%40"+mention+")%20"
    else:
        mention = ""
    
    # set start date
    if start_date:
        start_date = "since%3A"+start_date+"%20"
    else:
        start_date = ""
        
     # set end_date
    if end_date:
         end_date = "until%3A"+end_date+"%20"
    else:
         end_date = ""
         
    
    query_url = "https://twitter.com/search?q="  + sent_from + sent_to + mention + end_date + start_date + lang + '&src=typed_query&f=live'
     
    driver.get(query_url)
    sleep(random.uniform(1, 10))
    return


# read tweets on current page as webelement

def scrape_tweets_on_page(driver):
    page_cards =driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    return page_cards


# extract data from webdriver file
def extract_data_from_webelement(card):
    
    # twitter handle
    try:
         handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except:
        return
    
    # datetime of tweet 
    try:
        postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except:
        return
    
    # comment in tweet 
    try:
         comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    except:
        return
    
    # responding in tweeet
    try:
        respond = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except:
        return
    
    # tweet 
    tweet_tot_text = comment + respond
    
    # reply count
    try:
         reply_count = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
    except:
        return
    
    # retweet count
    try:
         retweet_count = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    except:
        return
    
    # like count
    try:
         like_count = card.find_element_by_xpath('.//div[@data-testid="like"]').text
    except:
        return
    
    # final concatination of all collected fields 
    tweet = [handle,postdate,tweet_tot_text,reply_count,retweet_count,like_count]
    
    return tweet

# function for scroll

def page_scroll(driver,max_scroll_try):
    scroll_end = False
    last_pos = driver.execute_script("return window.pageYOffset;")
    driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
    sleep(random.uniform(0, 15))
    cur_pos = driver.execute_script("return window.pageYOffset;")
    scroll_try = 0
    while cur_pos == last_pos:
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        scroll_try += 1 
        cur_pos = driver.execute_script("return window.pageYOffset;")
        if scroll_try > max_scroll_try:
            scroll_end = True
            break
    return  scroll_end


# Specify driver and output
def main_func(driver,scroll_check = 5,tweet_limit = 250):
    try:
        scroll_end = False
        page_count = 0
        tweet_collector =pd.DataFrame([])
        while  scroll_end == False:
            tweet_cards =scrape_tweets_on_page(driver)
            
            for c in range(len(tweet_cards)):
                tweet_list = extract_data_from_webelement(tweet_cards[c])    
                if not tweet_list:
                    continue
                df= pd.DataFrame([tweet_list],columns=('Handle','DataTime','Tweet','Reply_Count','Retweet_Count','Like_Count'))
                tweet_collector = tweet_collector.append(df)
                tweet_collector.drop_duplicates(subset=None, keep='first', inplace=False)
                

            scroll_end = page_scroll(driver,scroll_check)
            page_count += 1
            print("Currently Scraping page",page_count,"tweet count:",len(tweet_collector))
            if len(tweet_collector) > tweet_limit:
                scroll_end = True
    except:
        return tweet_collector

    return tweet_collector
    


driver = invoke_chrome_instance()

login_twitter("sandyma44414474","Tweet124$",driver)


advance_search(driver,mention='google',start_date = '2021-01-25',end_date ='2021-01-26')
google =main_func(driver,scroll_check = 5,tweet_limit= 25)
    
    



    
   
    
    
    
    

    

