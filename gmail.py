# -*- coding: utf_8 -*-
import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException,
)
from webdriver_manager.firefox import GeckoDriverManager

# 個別設定。
PROFILE = "./Profile"  # プロファイルのルートディレクトリを設定
LOGFILE = "check.log"  # ログファイルのパスを設定
GECKOLOG = "geckodriver.log"  # geckodriverのログファイルのパスを設定
SETTINGS = "https://mail.google.com/mail/u/0/#settings/accounts"  # GmailのURLを設定
WAITTIME = 20  # 次のクリックまでの待ち時間を設定


def write_log(message):
    with open(LOGFILE, "a") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')} {message}")


# ここからプログラム本文。
if __name__ == "__main__":
    os.environ["DISPLAY"] = ":99"  # 仮想ディスプレイの設定
    try:
        # FireFoxを起動し、Gmailの受信ボックスに移動する。
        options = Options()
        options.headless = True
        options.add_argument("--no-remote")
        options.add_argument("-profile")
        options.add_argument(PROFILE)
        options.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        )
        service = Service(GeckoDriverManager().install(), log_output=GECKOLOG)
        driver = webdriver.Firefox(service=service, options=options)
        driver.implicitly_wait(WAITTIME)

        # 上から順番にPOP3アカウントのポーリングを行う。
        print("GmailPopChecker", flush=True)
        while True:
            try:
                time.sleep(WAITTIME)
                driver.get(SETTINGS)
                if "Sign in - Google Accounts" in driver.title:
                    write_log("ログイン画面が表示されました。\n")
                    break
                WebDriverWait(driver, WAITTIME).until(EC.presence_of_element_located((By.XPATH, "//body")))
                tags = driver.find_elements(
                    By.XPATH, """//span[contains(.,'メールを今すぐ確認する')]"""
                )  # 英語なら「Check mail now」を探す。
                if len(tags):
                    for i, tag in enumerate(reversed(tags)):
                        try:
                            tag.click()
                        except (
                            StaleElementReferenceException,
                            ElementClickInterceptedException,
                            NoSuchElementException,
                        ) as e:
                            break
                else:
                    write_log("ボタンが見つかりませんでした。\n")
                    continue
            except WebDriverException as e:
                write_log(f"実行中エラー {type(e).__name__} - {e}")
                break
    except WebDriverException as e:
        write_log(f"起動時エラー {type(e).__name__} - {e}")
    finally:
        if "driver" in locals():
            driver.quit()
        write_log("終了しました。\n")
