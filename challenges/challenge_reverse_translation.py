import logging
import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from challenges.challenge_translate import challenge_translate
from challenges.utilities import get_sentence_in_hint_token, check_if_solution_in_db, insert_solution_into_db, contains


def challenge_reverse_translation(driver, db):
    table_name = "reverse"
    sentence_list = get_sentence_in_hint_token(driver)
    sentence = " ".join(sentence_list)
    existing_solution = check_if_solution_in_db(db, table_name, sentence)
    if existing_solution:

        # TODO
        # Find what's in the textaera here..
        print(f"Detected solution : {existing_solution}")
        existing_solution = set(existing_solution.split(" "))

    # neechallenge_translated to immplement

        # label class which contains text :
        label_contains = contains(driver, "label", "class", "_3f_Q3")
        logging.debug(label_contains)
        incomplete_sol: str = label_contains.text
        incomplete_sol = incomplete_sol.replace("\n", " ")
        incomplete_sol_set = set(incomplete_sol.split(" "))
        print("Possible solution ==> ")
        print(incomplete_sol_set - existing_solution)

        container_div = driver.find_element(By.XPATH,
                                            '//input[@data-test="challenge-text-input"]')



        # container_div = contains(driver, "div", "class", "_1FYT5")
        logging.debug(container_div)
        # input_field = contains(driver, "span", "class", "_1N3bb")
        # logging.debug(input_field)


    else:
        skip = driver.find_element(By.XPATH,
                                   '//button[@data-test="player-skip"]')
        skip.click()
        solution = driver.find_element(By.XPATH,
                                       '//div[contains(@class,"_1UqAr")]').text
        logging.debug(f"Adding Sentence {sentence} with solution {solution}")
        insert_solution_into_db(db, table_name, sentence, solution)

