import csv
import os
import platform
import random
import string
import subprocess
import sys
import warnings
import zipfile
from random import choice, uniform
from time import sleep

import requests
# import undetected_chromedriver as uc
from fake_headers import Headers
# from faker import Faker
from selenium import webdriver
from selenium.common.exceptions import (InvalidSessionIdException,
                                        NoSuchElementException,
                                        WebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from twocaptcha import TwoCaptcha

from . import proxy_config
from . import plugin_config

'''
Initialize the chrome options and return them only.
'''


__OSNAME__ = platform.system()


def initChromeDriver():
    try:
        # ?Get a random proxy
        proxy = proxy_config.getProxyList()
        proxy = proxy[random.randint(0, len(proxy)-1)]
        # proxy = proxy[2]

        proxy_split = proxy.split(":")
        PROXY_HOST = proxy_split[0]
        PROXY_PORT = proxy_split[1]
        PROXY_USER = proxy_split[2]
        PROXY_PASS = proxy_split[3]

        header = Headers(
            browser="chrome",
            os=__OSNAME__,
            headers=False
        ).generate()
        agent = header['User-Agent']

        options = webdriver.ChromeOptions()
        pluginfile = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", plugin_config.manifest_json)
            zp.writestr("background.js", plugin_config.background_js %
                        (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS))
        options.add_extension(pluginfile)
        #options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        prefs = {"profile.default_content_setting_values.notifications": 2, 'intl.accept_languages': 'en,en_US'}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile': {
                'password_manager_enabled': False
            }
        })
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-web-security")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--headless")
        # options.headless = True
        #viewport = ['2560,1440', '1920,1080', '1440,900']
        viewport = ['1228,947']
        options.add_argument(f"--window-size={choice(viewport)}")
        options.add_argument("--log-level=3")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f"user-agent={agent}")
        #! iniitialize the driver only where needed
        # driver = webdriver.Chrome(options=options)

        # wait = WebDriverWait(driver, 40)

        # print(driver)
        return options

    except Exception as e:
        print(e)
        return False


def type_me(element, text):
    """
    Type like a human
    """
    print('Typing : {}'.format(text))
    for letter in text:
        element.send_keys(letter)
        sleep(uniform(.0, .0))

#!DEBUG
# initChromeDriver()
