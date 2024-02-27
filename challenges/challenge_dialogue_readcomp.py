import logging

from selenium.webdriver.common.by import By

from challenges.utilities import get_sentence_in_hint_token, check_if_solution_in_db, validate_and_continue, \
    insert_solution_into_db, solve_simple_challenge


# Check if we can use solve_simple_challenge here
def challenge_dialogue_readcomp(driver, db, isDial):
    table_name = "dialogue"
    solve_simple_challenge(driver, db, table_name)

    # sentence_list = get_sentence_in_hint_token(driver)
    # sentence = " ".join(sentence_list)
    # print(f"Detected Sentence : {sentence}")

    # existing_solution = check_if_solution_in_db(db, table_name, sentence)
    #
    # if existing_solution:
    #     logging.debug(f"Existing solution found: {existing_solution}")
    #
    #     choices = driver.find_elements(By.XPATH,
    #                                    '//span[@data-test="challenge-judge-text"]')
    #     for choice in choices:
    #         if choice.text == existing_solution:
    #             choice.click()
    #             break
    #
    #     validate_and_continue(driver)
    #
    # else:
    #     skip = driver.find_element(By.XPATH,
    #                                '//button[@data-test="player-skip"]')
    #     skip.click()
    #     solution = driver.find_element(By.XPATH,
    #                                    '//div[contains(@class,"_1UqAr")]').text
    #     logging.debug(f"Adding Sentence {sentence} with solution {solution}")
    #     insert_solution_into_db(db, table_name, sentence, solution)
