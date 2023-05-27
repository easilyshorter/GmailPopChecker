# -*- coding: utf_8 -*-
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import StaleElementReferenceException

#個別設定。
PROFILE = "./Profile" #プロファイルのフォルダを設定
WAITTIME = 12 #最大待ち時間を設定
ACCOUNTS = 5 #POP3のアカウント数を設定

#FireFoxを起動し、Gmailの受信ボックスに移動する。
options = Options()
options.add_argument("--headless")
options.add_argument("-profile")
options.add_argument(PROFILE)
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(WAITTIME)
driver.get("https://mail.google.com/mail/u/0/#inbox")
print("これよりPOP3アカウントのポーリングを行います。")
time.sleep(WAITTIME)

#上から順番にPOP3アカウントのポーリングを行う。(英語なら「Check mail now」を探す。)
i = 0
while True:
    driver.get("https://mail.google.com/mail/u/0/#settings/accounts")
    tag = driver.find_elements(By.XPATH, """//span[contains(.,'メールを今すぐ確認する')]""")
    n = len(tag)
    t = datetime.datetime.now()
    if n != ACCOUNTS:
        print(t.strftime("%Y%m%d%H%M%S"), "%d個の中の%d番目のポーリングに無視しました。" % (n, i+1), flush=True)
        continue
    try:
        tag[i].click()
        print(t.strftime("%Y%m%d%H%M%S"), "%d個の中の%d番目のポーリングに成功しました。" % (n, i+1), flush=True)
    except StaleElementReferenceException:
        print(t.strftime("%Y%m%d%H%M%S"), "%d個の中の%d番目のポーリングに失敗しました。" % (n, i+1), flush=True)
    i += 1
    if i == ACCOUNTS:
        i = 0
    time.sleep(WAITTIME)
driver.quit()
