"""A selenium module for clocking in and out.

This module uses the selenium chrome webdriver to connect to
Apollo HR XE clock system as of 2020/6/8.
"""
import datetime
from enum import Enum
from math import ceil
from typing import NewType

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_LOGIN = "https://auth.mayohr.com/HRM/Account/Login"
URL_CLOCK = "https://apolloxe.mayohr.com/ta?id=webpunch"
URL_SCHEDULE = "https://apolloxe.mayohr.com/ta/personal/shiftschedule"

class ClockType(Enum):
    clock_in = "in"
    clock_out = "out"

IClockType = NewType('IClockType', ClockType)

class ApolloSession:
    """This class represents a single browser session."""

    def __init__(self):
        """Start the webdriver session."""
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        assert opts.headless  # Operating in headless mode
        self.browser = Chrome(options=opts)
        self.logged_in = False

    def __enter__(self):
        """Allow for usage using with."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Allow for usage using with, cleaning up the browser session on exit."""
        self.browser.quit()

    def __del__(self):
        """Clean up browser session on variable delete."""
        self.browser.quit()

    def login(self, user: str, pwd: str):
        """Perform login.

        Arguments:
            user:str - username
            pwd:str - password
        """
        self.browser.get(URL_LOGIN)
        delay = 30  # seconds
        try:
            _ = WebDriverWait(self.browser, delay).until(
                EC.presence_of_element_located((By.NAME, "userName"))
            )
        except TimeoutException:
            return "Error: Loading took too much time!"
        username = self.browser.find_element_by_name("userName")
        password = self.browser.find_element_by_name("password")
        username.send_keys(user)
        password.send_keys(pwd)
        submit = self.browser.find_element_by_class_name("submit-btn")
        submit.submit()
        try:
            _ = WebDriverWait(self.browser, delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-menu__welcome"))
            )
        except TimeoutException:
            return "Error: Loading took too much time!"
        self.logged_in = True
        return True

    def clock(self, clock_type: IClockType):
        """Perform clock-in. Requires login.

        Arguments:
            clock_type:str - "in" or "out", no other choices will work.
        """
        if self.logged_in:
            self.browser.get(URL_CLOCK)
            delay = 30  # seconds
            try:
                _ = WebDriverWait(self.browser, delay).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ta_btn_cancel"))
                )
            except TimeoutException:
                return "Error: Loading took too much time!"
            btns = self.browser.find_elements_by_class_name("ta_btn_cancel")
            first_btn = btns[0]
            if ((first_btn.text == "on duty") and (clock_type == "in")) or (
                (first_btn.text == "clock out") and (clock_type == "out")
            ):
                first_btn.click()
                try:
                    _ = WebDriverWait(self.browser, delay).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h4"))
                    )
                except TimeoutException:
                    return "Error: Loading took too much time!"
                els = self.browser.find_elements_by_tag_name("h4")
                return els[0].text
            if clock_type == "in":
                return (
                    "Error: on duty button not available! Current button text is "
                    + first_btn.text
                )
            if clock_type == "out":
                return (
                    "Error: clock out button not available! Current button text is "
                    + first_btn.text
                )
        return "Error: not logged in."

    def clock_in(self):
        """Alias to clock in."""
        return self.clock(ClockType.clock_in)

    def clock_out(self):
        """Alias to clock out."""
        return self.clock(ClockType.clock_out)

    def work_day_query(self):
        """Look up today's date on the schedule to see if it is a work day. Requires login."""
        if self.logged_in:
            self.browser.get(URL_SCHEDULE)
            delay = 30  # seconds
            try:
                _ = WebDriverWait(self.browser, delay).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "schedule-info__time")
                    )
                )
            except TimeoutException:
                return "Error: Loading took too much time!"
            today = datetime.datetime.today()
            day_of_week = (today.weekday() + 1) % 7
            first_day = today.replace(day=1)
            dom = today.day
            adjusted_dom = dom + ((first_day.weekday() + 1) % 7)
            week_of_month = int(ceil(adjusted_dom / 7.0))
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
