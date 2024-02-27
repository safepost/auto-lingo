import itertools
import logging
import sqlite3
import time

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.common.by import By

from challenges.utilities import remove_punct, insert_solution_into_db, check_if_solution_in_db, validate_and_continue


def challenge_tap_complete(driver: webdriver, db: sqlite3.Connection):
    db_name = "tap_complete"
    print("---> challenge_tap_complete")

    sentence_tokens = driver.find_elements(By.XPATH,
                                           '//div[@data-test="hint-token"]')
    sentence_tokens_text = [s.get_attribute("aria-label") for s in sentence_tokens]
    sentence = " ".join(sentence_tokens_text)


    print(f"Detected sentence : {sentence}")

    existing_solution: str = check_if_solution_in_db(db, db_name, sentence)
    if existing_solution:
        logging.debug(f"Existing solution found: {existing_solution}")
        # detect if // in existing solution and then clic on many solutions ?
        tap_tokens = driver.find_elements(By.XPATH,
                                          '//span[@data-test="challenge-tap-token-text"]')
        soluces = existing_solution.split("//")
        for s in soluces:
            for tap_token in tap_tokens:
                if tap_token.text == s:
                    tap_token.click()
                    break

        validate_and_continue(driver)

    else: # this is when it can not quickly solve it.
        logging.debug("No solution found in DB")

        # Try a q&d solution
        # Verify that solution is on blanks !! So we only need to capture -challenge-tap-token
        # get what's before
        # find associated tap tokens
        # and tap on it
        # sols = driver.find_elements((By.XPATH, '//button[contains(@data-test,"-challenge-tap-token")]'))
        # tap_tokens = driver.find_elements(By.XPATH,
        #                                   '//span[@data-test="challenge-tap-token-text"]')
        # for s in sols:
        #     token_sol = s.get_attribute("data-test")
        #     find_me = token_sol.replace("-challenge-tap-token","")
        #     for t in tap_tokens:
        #         if remove_punct(t.text) == remove_punct(find_me):
        #             t.click()
        # validate_and_continue(driver)

        #
        #"data-test="Is this-challenge-tap-token""


        try:
            skip = driver.find_element(By.XPATH,
                                   '//button[@data-test="player-skip"]')
            skip.click()
        except NoSuchElementException:
            # No Skip :)
            # Find somewhere to clic ?
            tap_tokens = driver.find_elements(By.XPATH,
                                              '//span[@data-test="challenge-tap-token-text"]')
            for tap_token in tap_tokens:
                # Clic on the first token
                tap_token.click()
                break

            logging.debug("Finding validation button")
            validation_button = driver.find_element(By.XPATH, '//button[@data-test="player-next"]')
            validation_button.click()



        # print(skip.text)


        #TODO

        # First identify which token can be accepted as solution
        tap_tokens = driver.find_elements(By.XPATH,
                                          '//span[@data-test="challenge-tap-token-text"]')

        solution = driver.find_element(By.XPATH,
                                       '//div[contains(@class,"_1UqAr")]').text

        # Select tap token that fits the solution
        good_tokens = []
        for t in tap_tokens:
            if remove_punct(t.text) in remove_punct(solution):
                if t.text != "":
                    logging.debug(f"Adding {t.text} as good token")
                    good_tokens.append(t)

        # Kept good tokens
        print([g.text for g in good_tokens])

        # Ordering token
        index = {}
        for g in good_tokens:
            _g = g.text
            index[_g] = remove_punct(solution).index(remove_punct(_g))
            print(f"Index of {_g} was {index[_g]} in {remove_punct(solution)}")

        print(index)
        good_order = {k: v for k, v in sorted(index.items(), key=lambda item: item[1])}
        print(good_order)
        # Now just insert tokens as a list in DB (coma separated ? hope we can)

        if len(good_order.keys()) > 1:
            solution = "//".join(good_order.keys())
        else:
            # Get first key
            solution = next(iter(good_order))


        # error class = _1x6Dk  ?
        print(f"Solution : {solution}")
        # solution_list = [remove_punct(s) for s in solution.split(" ")]
        # print(f"Tokens : {sentence_tokens_text}")
        # # bad logic
        #
        # remaining_token = set(solution_list) - set(sentence_tokens_text)
        # possible_solution = remaining_token.pop()
        # print(f"POssible solution : {possible_solution}")

        # dictionary[sentence] = possible_solution
        print(f"Adding sentence : {sentence} with solution {solution}")

        # DB management
        # cur = db.cursor()
        insert_solution_into_db(db, db_name, sentence, solution)


def challenge_tap(driver, dictionary):
    print("---> challenge_tap")
    sentence_tokens = driver.find_elements(By.XPATH,
                                           '//div[@class="hint-token"]')
    # sentence = driver.find_element(By.XPATH,
    #                                '//div[@class="_1eXoV _3ZoSe"]').text
    sentence_tokens_text = [s.text for s in sentence_tokens]
    sentence = " ".join(sentence_tokens_text)

    # sentence = driver.find_element(By.XPATH,
    #                                '//div[@class="_3NgMa _2Hg6H"]').text
    print(f"Detected sentence : {sentence}")
    sentence += " (ta)"
    if sentence in dictionary:
        choices = driver.find_elements(By.XPATH,
                                       '//div[@class="_1yW4j _2LmyT"]')
        words = dictionary[sentence].split()
        for word in words:
            for choice in choices:
                if choice.text == word:
                    choice.click()
    else:
        skip = driver.find_element(By.XPATH,
                                   '//button[@data-test="player-skip"]')
        print(skip.text)
        skip.click()
        solution = driver.find_element(By.XPATH,
                                       '//div[@class="_1UqAr _1sqiF"]').text
        solution = solution.replace(".", "").replace("?", "").replace(
            "!", "").replace(";", "").replace(",", "").replace("¿", "")
        dictionary[sentence] = solution
        # print(sentence, '-ta->', dictionary[sentence])