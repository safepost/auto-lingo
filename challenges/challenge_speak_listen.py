from selenium.webdriver.common.by import By

from challenges.utilities import wait_element


def challenge_speak_listen(driver):
    skip = wait_element(driver, '//button[@data-test="player-skip"]')
    skip.click()

    next = driver.find_element(By.XPATH, '//button[@data-test="player-next"]')
    next.click()