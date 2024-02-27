import logging

from selenium.webdriver.common.by import By


def challenge_form(driver, dictionary):
    logging.debug("never seen before")
    sentence = driver.find_element(By.XPATH,
                                   '//div[@data-test="challenge-form-prompt"]').get_attribute('data-prompt')
    sentence += " (f)"
    if sentence in dictionary:
        choices = driver.find_elements(By.XPATH,
                                       '//div[@data-test="challenge-judge-text"]')

        for choice in choices:
            if choice.text == dictionary[sentence]:
                choice.click()
    else:
        skip = driver.find_element(By.XPATH,
                                   '//button[@data-test="player-skip"]')
        skip.click()
        solution = driver.find_element(By.XPATH,
                                       '//div[@class="_1UqAr _1sqiF"]')
        dictionary[sentence] = solution.text
        # print(sentence, '-x->', dictionary[sentence])