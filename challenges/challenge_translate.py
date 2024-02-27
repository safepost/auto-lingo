import logging
import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import webdriver

from challenges.utilities import get_sentence_in_hint_token, remove_punct, remove_punct_smart, check_if_solution_in_db, \
    insert_solution_into_db, validate_and_continue, remove_useless_punct, contains


def challenge_translate(driver: webdriver, db, table_name="translate"):
    # db_name = "translate"

    print("Into Challenge translate")
    try:
        sentence_list = get_sentence_in_hint_token(driver)
    except Exception as err:
        print(err)
        print("Sentence list not found ! Maybe not ready yet ?")
    print(sentence_list)
    sentence = " ".join(sentence_list)
    print(f"Detected Sentence : {sentence}")
    # sentence = driver.find_element(By.XPATH,
    #                                '//span[@data-test="hint-sentence"]').text
    # print(f"Legacy sentence {sentence}")
    # sentence += " (t)"
    existing_solution = check_if_solution_in_db(db, table_name, sentence)
    if existing_solution:
        logging.debug(f"Existing solution found: {existing_solution}")

        tap_tokens = driver.find_elements(By.XPATH,
                                          '//button[contains(@data-test,"challenge-tap-token")]')
        logging.debug(f"Detected tap tokens: {[t.text for t in tap_tokens]}")
        # check if the challenge is tap tokens
        if len(tap_tokens) > 0:
            # get solution without dot at the end
            # remove commas, dots, marks and change string to lowercase
            # solution = existing_solution.replace(".", "").replace(",", "").replace("!", "").replace("?", "").replace(";", "").lower()
            solution = remove_useless_punct(existing_solution)
            logging.debug(f"Existing solution update : {solution}")

            # we probably have langage dependecies here ...
            # TODO be inclusive and add more token that we have
            solution = solution.replace("'", " ").replace("-", " ")

            # solution = solution.replace("-", " ")

            # challenge_translate.apostrophe_counter = (
            #     challenge_translate.apostrophe_counter + 1) % 2
            # challenge_translate.dash_counter = (
            #     challenge_translate.dash_counter + 1) % 4

            logging.debug(f"Modified solution: {solution}")
            words = solution.lower().split(" ")

            for word in words:
                for tap_token in tap_tokens:
                    if tap_token.get_attribute("aria-disabled") != "false":
                        continue
                    if remove_punct(tap_token.text).lower() == word:
                        tap_token.click()
                        break
        else:
            input_field = driver.find_element(By.XPATH,
                                              '//textarea[@data-test="challenge-translate-input"]')
            input_field.send_keys(existing_solution)
            input_field.send_keys(Keys.RETURN)

        validate_and_continue(driver)

    else:
        logging.debug("No solution found in DB")
        skip = driver.find_element(By.XPATH,
                                   '//button[@data-test="player-skip"]')
        skip.click()
        solution = driver.find_element(By.XPATH,
                                       '//div[contains(@class,"_1UqAr")]').text
        # solution = remove_punct_smart(solution)
        # solution = solution.replace(";", "").replace("¿", "").replace("¡", "")
        logging.debug(f"Adding Sentence {sentence} with solution {solution}")
        insert_solution_into_db(db, table_name, sentence, solution)

        # dictionary[sentence] = solution
        # print(sentence, '--->', dictionary[sentence])
