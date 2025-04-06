# -*- coding: utf_8 -*-
import os
import time
import datetime
import random
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

# 設定項目。
DEBUG = False  # デバッグモードを有効にするかどうかを設定
PROFILE = "./Profile"  # プロファイルのルートディレクトリを設定
LOGFILE = "./log/check.log"  # ログファイルのパスを設定
GECKOLOG = "./log/geckodriver.log"  # geckodriverのログファイルのパスを設定
GECKODIR = "/usr/local/bin/geckodriver"  # geckodriverのパスを設定
SETTINGS = "https://mail.google.com/mail/u/0/#settings/accounts"  # GmailのURLを設定
WAITTIME = 20  # 次のクリックまでの基本待ち時間(この後追加でWAITTIME以下の秒数待つ)を設定
WAITLONG = 90  # 夜中の時間帯の長い待ち時間を設定
NIGHTMIN = 1  # 夜中の時間帯の開始時間を設定
NIGHTMAX = 7  # 夜中の時間帯の終了時間を設定
HEADLESS = True  # ヘッドレスモードを有効にするかどうかを設定


# ログファイルのディレクトリを作成する。
def write_log(message):
    with open(LOGFILE, "a") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')} {message}")


# ここからプログラム本文。
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.environ["DISPLAY"] = ":99"  # 仮想ディスプレイの設定
    try:
        # FireFoxを起動し、Gmailの受信ボックスに移動する。
        options = Options()
        options.headless = HEADLESS
        options.add_argument("--no-remote")
        options.add_argument("-profile")
        options.add_argument(PROFILE)
        options.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
        )
        service = Service(GECKODIR, log_output=GECKOLOG)
        driver = webdriver.Firefox(service=service, options=options)
        driver.implicitly_wait(WAITLONG)

        # 上から順番にPOP3アカウントのポーリングを行う。
        while True:
            try:
                if NIGHTMIN <= datetime.datetime.now().hour < NIGHTMAX:
                    time.sleep(WAITLONG + random.uniform(0, WAITLONG))
                else:
                    time.sleep(WAITTIME + random.uniform(0, WAITTIME))
                driver.get(SETTINGS)
                if "Sign in - Google Accounts" in driver.title:
                    write_log("❌ ログイン画面が表示されました。\n")
                    break
                WebDriverWait(driver, WAITTIME).until(EC.presence_of_element_located((By.XPATH, "//body")))
                tags_check = driver.find_elements(
                    By.XPATH, """//span[contains(.,'メールを今すぐ確認する')]"""
                )  # 英語なら「Check mail now」を探す。
                if len(tags_check):
                    if DEBUG:
                        tags_history = driver.find_elements(By.XPATH, """//span[contains(.,'履歴を表示')]""")
                        if len(tags_history) == len(tags_check):
                            write_log(
                                f"❓ ボタンが{len(tags_history)}個のうち{len(tags_check)}個しか見つかりませんでした。\n"
                            )
                        else:
                            write_log(f"✔️ ボタンが{len(tags_check)}個見つかりました。\n")
                    for i, tag in enumerate(reversed(tags_check)):
                        try:
                            tag.click()
                        except (
                            StaleElementReferenceException,
                            ElementClickInterceptedException,
                            NoSuchElementException,
                        ) as e:
                            break
                else:
                    write_log("⚠️ ボタンが見つかりませんでした。\n")
                    continue
            except WebDriverException as e:
                write_log(f"❌ 実行中エラー {type(e).__name__} - {e}")
                break
    except WebDriverException as e:
        write_log(f"❌ 起動時エラー {type(e).__name__} - {e}")
    finally:
        if "driver" in locals():
            driver.quit()
        write_log("🙏 終了しました。\n")
