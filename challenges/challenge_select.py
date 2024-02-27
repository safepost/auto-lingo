import logging
import sqlite3

from selenium.webdriver.common.by import By

from challenges.utilities import check_if_solution_in_db, insert_solution_into_db, validate_and_continue


def challenge_select(driver, db: sqlite3.Connection):
    table_name = "challenge_select"
    print("Challenge select")
    sentence = driver.find_element(By.XPATH,
                                   '//h1[@data-test="challenge-header"]').text

    sentence = sentence.replace("« ", "").replace(" »", "")
    logging.debug(f"Found sentence : {sentence}")
    existing_solution = check_if_solution_in_db(db, table_name, sentence)

    if existing_solution:
        logging.debug(f"Existing solution found: {existing_solution}")
        choices = driver.find_elements(By.XPATH, '//span[@class="HaQTI"]')
        print(f"Choices : {choices}")

        for choice in choices:
            if choice.text == existing_solution:
                choice.click()
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
                                       '//div[@class="_1UqAr _3Qruy"]').text
        print("Found soluce ")
        insert_solution_into_db(db, table_name, sentence, solution)

        # dictionary[sentence] = solution
        logging.debug(f"Adding {sentence} = {solution} to DB")
        # print(sentence, '-o->', dictionary[sentence])