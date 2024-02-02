
from flask import Blueprint, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, re

twitter_module = Blueprint("twitter_module", __name__)

@twitter_module.route("/twitter_result", methods=["POST"])
def twitter_result():
    class SNSProfileScraper:
        def __init__(self, username , driver_path):
            self.driver_path = driver_path
            self.username = username

        def scrape_twitter_profile(self):
            try:
                url = 'https://twitter.com/' + self.username
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                driver = webdriver.Chrome(executable_path=self.driver_path, options=options)
                driver.get(url)
                time.sleep(5)
                try:                
                    name = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div.css-1dbjc4n.r-aqfbo4.r-gtdqiz.r-1gn8etr.r-1g40b8q > div:nth-child(1) > div > div > div > div > div > div.css-1dbjc4n.r-16y2uox.r-1wbh5a2.r-1pi2tsx.r-1777fci > div > h2 > div > div > div > div > span.css-901oao.css-16my406.r-1awozwy.r-18jsvk2.r-6koalj.r-poiln3.r-b88u0q.r-bcqeeo.r-1udh08x.r-3s2u2q.r-qvutc0 > span > span:nth-child(1)')
                    name = name.text
                except:
                    name = None

                try:
                    screen_name = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div.css-1dbjc4n.r-6gpygo.r-14gqq1x > div.css-1dbjc4n.r-1wbh5a2.r-dnmrzs.r-1ny4l3l > div > div.css-1dbjc4n.r-1awozwy.r-18u37iz.r-1wbh5a2 > div > div > div > span')
                    screen_name = screen_name.text
                except:
                    screen_name = 'None'

                try:
                    bio = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div:nth-child(3) > div > div > span')
                    bio = bio.text
                except:
                    bio = None

                try:
                    location = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div:nth-child(4) > div > span:nth-child(1) > span > span')
                    location = location.text
                except:
                    location = None

                try:
                    profile_img = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div.css-1dbjc4n.r-1habvwh.r-18u37iz.r-1w6e6rj.r-1wtj0ep > div.css-1dbjc4n.r-1adg3ll.r-16l9doz.r-6gpygo.r-2o1y69.r-1v6e3re.r-bztko3.r-1xce0ei > div.r-1p0dtai.r-1pi2tsx.r-1d2f490.r-u8s1d.r-ipm5af.r-13qz1uu > div > div.r-1p0dtai.r-1pi2tsx.r-1d2f490.r-u8s1d.r-ipm5af.r-13qz1uu > div > a > div.css-1dbjc4n.r-14lw9ot.r-sdzlij.r-1wyvozj.r-1udh08x.r-633pao.r-u8s1d.r-1v2oles.r-desppf > div > div.r-1p0dtai.r-1pi2tsx.r-1d2f490.r-u8s1d.r-ipm5af.r-13qz1uu > div > img')
                    profile_img = profile_img.get_attribute('src')
                except:
                    url = None

                try:
                    joined_date = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div:nth-child(4) > div > span.css-901oao.css-16my406.r-14j79pv.r-4qtqp9.r-poiln3.r-1b7u577.r-bcqeeo.r-qvutc0 > span')
                    joined_date = joined_date.text
                except:
                    joined_date = None

                try:
                    profile_data = {
                        'sns' : 'twitter',
                        'name': name,
                        'screen_name': screen_name,
                        'bio': bio,
                        'location': location,
                        'profile_img': profile_img,
                        'joined_date': joined_date
                    }
                    return profile_data
                except:
                    return None
            except:
                return None

    
    
    driver_path = 'app/chromedriver.exe'

    find_name = request.cookies.get("NAME")

    scraper = SNSProfileScraper(find_name , driver_path)
    twitter_profile = scraper.scrape_twitter_profile()

    result ={}

    result['twitter'] = twitter_profile
    
    return render_template("twitter_result.html", result=result)