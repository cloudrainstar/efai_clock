from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import datetime
from math import ceil
from time import sleep

class ApolloSession:
    def __init__(self):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        assert opts.headless  # Operating in headless mode
        self.browser = Chrome(options=opts)
        self.logged_in = False
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.browser.quit()
        
    def __del__(self):
        self.browser.quit()
        
    def login(self, user:str, pwd:str):
        self.browser.get('https://auth.mayohr.com/HRM/Account/Login')
        delay = 10 # seconds
        try:
            myElem = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.NAME, 'userName')))
        except TimeoutException:
            return "Error: Loading took too much time!"
        username = self.browser.find_element_by_name("userName")
        password = self.browser.find_element_by_name("password")
        username.send_keys(user)
        password.send_keys(pwd)
        submit = self.browser.find_element_by_class_name("submit-btn")
        submit.submit()
        try:
            myElem = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'user-menu__welcome')))
        except TimeoutException:
            return "Error: Loading took too much time!"
        self.logged_in = True
        return True
        
    def clock(self, clock_type):
        if self.logged_in:
            self.browser.get('https://hrm.mayohr.com/ta?id=webpunch')
            delay = 10 # seconds
            try:
                myElem = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'ta_btn_cancel')))
            except TimeoutException:
                return "Error: Loading took too much time!"
            btns = self.browser.find_elements_by_class_name("ta_btn_cancel")
            first_btn = btns[0]
            if ((first_btn.text == 'on duty') and (clock_type == "in")) or ((first_btn.text == 'clock out') and (clock_type == "out")):
                first_btn.click()
                try:
                    myElem = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.TAG_NAME, 'h4')))
                except TimeoutException:
                    return "Error: Loading took too much time!"
                els = self.browser.find_elements_by_tag_name("h4")
                return els[0].text
            if clock_type == "in":
                return "Error: on duty button not available! Current button text is " + first_btn.text
            if clock_type == "out":
                return "Error: clock out button not available! Current button text is " + first_btn.text
        return "Error: not logged in."
        
    def clock_in(self):
        return self.clock("in")
    
    def clock_out(self):
        return self.clock("out")
        
    def work_day_query(self):
        if self.logged_in:
            self.browser.get('https://hrm.mayohr.com/ta/personal/shiftschedule')
            delay = 10 # seconds
            try:
                myElem = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'schedule-info__time')))
            except TimeoutException:
                return "Error: Loading took too much time!"
            day_of_week = datetime.datetime.today().weekday() + 1 % 7
            first_day = datetime.datetime.today().replace(day=1)
            dom = datetime.datetime.today().day
            adjusted_dom = dom + first_day.weekday()
            week_of_month = int(ceil(adjusted_dom/7.0))
            els_table = self.browser.find_elements_by_tag_name("table")
            els_tr = els_table[0].find_elements_by_tag_name("tr")
            els_td = els_tr[week_of_month].find_elements_by_tag_name("td")
            date_square = els_td[day_of_week]
            leave_pic = len(date_square.find_elements_by_class_name("leavePic")) > 0
            if leave_pic:
                return "leave"
            if "0800-1700" in date_square.text.split("\n"):
                return "work"
            return "off"
        else:
            return "error"
