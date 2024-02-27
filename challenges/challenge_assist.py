import logging
import sqlite3
import time

from selenium.webdriver.common.by import By

from challenges.utilities import check_if_solution_in_db, insert_solution_into_db, validate_and_continue


def challenge_assist(driver, db: sqlite3.Connection):
    db_name = "assist"
    print("Challenge assist")
    sentence = driver.find_element(By.XPATH,
                                   '//div[@class="_1KUxv _11rtD"]').text

    print(f"Found sentence : {sentence}")
    existing_solution = check_if_solution_in_db(db, db_name, sentence)
    if existing_solution:
        logging.debug(f"Existing solution found: {existing_solution}")
        choices = driver.find_elements(By.XPATH, '//span[@data-test="challenge-judge-text"]')
        logging.debug(f"Choices: {[c.text for c in choices]}")

        for choice in choices:
            if choice.text == existing_solution:
                choice.click()
                # Validation
                validate_and_continue(driver)
                break

    else:
        logging.debug("No solution found in DB")
        skip = driver.find_element(By.XPATH,
                                   '//button[@data-test="player-skip"]')
        print("Finding Skip button")
        skip.click()
        print("Clicked on skip")
        solution = driver.find_element(By.XPATH,
                                       '//div[contains(@class,"_1UqAr")]').text
        print(f"Found soluce : {solution} ")
        # dictionary[sentence] = solution
        logging.debug(f"Adding {sentence} = {solution} to DB :)")
        insert_solution_into_db(db, db_name, sentence, solution)

        # print(sentence, '-o->', dictionary[sentence])