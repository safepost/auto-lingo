import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


def challenge_name(driver, dictionary):
    print("never seen before")
    sentence = driver.find_element(By.XPATH,
                                   '//h1[@data-test="challenge-header"]').text
    sentence += " (n)"
    if sentence in dictionary:
        input_field = driver.find_element(By.XPATH,
                                          '//input[@data-test="challenge-text-input"]')
        input_field.send_keys(dictionary[sentence])
        input_field.send_keys(Keys.RETURN)

    else:
        skip = driver.find_element(By.XPATH,
                                   '//button[@data-test="player-skip"]')
        skip.click()
        time.sleep(0.2)
        solution = driver.find_element(By.XPATH,
                                       '//div[@class="_1UqAr _1sqiF"]').text

        correct_solution_solutions = driver.find_element(By.XPATH,
                                                         '//h2[@class="_1x6Dk _1sqiF"]').text
        if "solutions" in correct_solution_solutions:
            solution = solution.split(",")[0]

        dictionary[sentence] = solution
        # print(sentence, '-+->', dictionary[sentence])