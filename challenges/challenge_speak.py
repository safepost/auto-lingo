import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import pyttsx3
from pydub import AudioSegment

from selenium.webdriver.chrome.service import Service as ChromeService
# https://stackoverflow.com/questions/963503/how-to-save-text-to-speech-as-a-wav-with-microsoft-sapi

# We have no solution yet for this challenge because we need text2speach with WAV
# and we only found MP3 compatible

if __name__ == "__main__":

    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices")[0]
    engine.setProperty('voice', voices)
    text = 'Your Text Your Text Your Text Your Text Your Text Your Text Your Text Your TextYour Text Your Text Your TextYour TextYour TextYour TextYour Text Your TextYour TextYour TextYour TextYour TextYour TextYour TextYour TextYour TextYour TextYour TextYour TextYour TextYour TextYour Text'
    engine.save_to_file(text, 'challenge.mp3')
    engine.runAndWait() # don't forget to use this line

    sound = AudioSegment.from_mp3('D:\\Dev_perso\\autoduo\\auto-lingo\\challenges\\challenge.mp3')
    sound.export("challenge.wav", format="wav")

    path = 'D:\\Dev_perso\\autoduo\\auto-lingo\\challenges\\challenge.wav'

    service = ChromeService(executable_path="D:\\Dev_perso\\chromedriver-win64\\chromedriver.exe")
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--allow-file-access-from-files")
    chrome_options.add_argument("--use-file-for-fake-audio-capture={0}".format(path))

    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get('https://www.google.com/intl/pl/chrome/demos/speech.html')
    select = Select(driver.find_element(By.XPATH, '//*[@id="select_language"]'))
    select.select_by_visible_text('English')
    driver.find_element(By.XPATH, '//*[@id="start_button"]').click()
    time.sleep(10)