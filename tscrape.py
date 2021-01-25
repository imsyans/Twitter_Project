# Install chromedriver for selenium to work
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import chromedriver_autoinstaller
import pandas as pd
from time import sleep 
import datetime as dt

# creating a chrome instance 
def invoke_chrome_instance():
    driver_path = chromedriver_autoinstaller.install()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f'user-agent={UserAgent}')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--window-size=1920,1200");
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path = driver_path,options=chrome_options)
    sleep(3)
    driver.get("https://twitter.com/login")
    print(driver.title)
    driver.get_screenshot_as_file("test.png")
    return driver


# function to login to twitter
def login_twitter(username,password,driver):
    try: 
        driver.get("https://twitter.com/login")
        sleep(3)
        path_username = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
        path_username.send_keys(username)
        path_password = driver.find_element_by_xpath('//input[@name="session[password]"]')
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
         
    
    query_url = "https://twitter.com/search?q="  + sent_from + sent_to + mention + lang + end_date + start_date  + '&src=typed_query&f=live'
     
    driver.get(query_url)
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
    

chrome_tab = invoke_chrome_instance()

login_twitter("sandyma44414474","Tweet124$",chrome_tab)

tweet_collector =pd.DataFrame([])

advance_search(chrome_tab,mention='Hello')


tweet_cards =scrape_tweets_on_page(chrome_tab)

for c in range(len(tweet_cards)):
    tweet_list = extract_data_from_webelement(tweet_cards[c])
    if not tweet_list:
        continue
    df= pd.DataFrame([tweet_list],columns=('Handle','DataTime','Tweet','Reply_Count','Retweet_Count','Like_Count'))
    tweet_collector = tweet_collector.append(df)
 
tweet_collector =tweet_collector.drop_duplicates(subset=None, keep='first', inplace=False)


tweet_collector.index = pd.RangeIndex(len(tweet_cards))

chrome_tab.close()
