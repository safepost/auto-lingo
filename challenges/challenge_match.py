import logging
import sqlite3
import time

from selenium.webdriver.common.by import By

from challenges.utilities import check_if_solution_in_db, insert_solution_into_db, validate_and_continue


def challenge_match(driver, db: sqlite3.Connection):
    table_name = "match"
    print("Challenge match")
    # tap_tokens = driver.find_elements(By.XPATH,
    #                                   '//span[@data-test="challenge-tap-token-text"]')
    # print(f"Detected tap tokens : {tap_tokens}")

    tap_tokens = driver.find_elements(By.XPATH,
                                      '//button[contains(@data-test,"challenge-tap-token")]')
    # print([t.text.split("\n")[1] for t in tap_tokens_buttons])

    tap_token1 = tap_tokens[:5]
    tap_token2 = tap_tokens[5:]

    mapping_tap = {}
    for t in tap_tokens:
        logging.debug(t.text)
        mapping_tap[t.text.split("\n")[1]] = t

    logging.debug(f'Tap token text : {mapping_tap.keys()}')
    for token in tap_token1:
        existing_solution = check_if_solution_in_db(db, table_name, token.text.split("\n")[1])
        if existing_solution:
            logging.debug(f"Existing solution found: {existing_solution}")
            token.click()
            if existing_solution in mapping_tap:
                mapping_tap[existing_solution].click()
                continue
            else:
                logging.debug("Do we have multiple translations for the same word ?!")

        if token.get_attribute("aria-disabled") != "false":
            logging.debug(f'Token attributes : {token.get_attribute("aria-disabled")} {token.get_attribute("disabled")} ')
            continue

        invalid_tokens = []

        for token2 in tap_token2:
            token.click()
            time.sleep(.1) # Click slower
            if token2 in invalid_tokens or token2.get_attribute("aria-disabled") != "false":
                # This one has been tried, move on to the next instance of the loop
                continue
            else:
                invalid_tokens.append(token2)
                print(f"Two: {token2.text}")
                time.sleep(.1) # Click slower
                token2.click()

                if token2.get_attribute("aria-disabled") != "false":
                    print("Inserting solution in DB")
                    insert_solution_into_db(db, table_name, token.text.split("\n")[1], token2.text.split("\n")[1])
                    break

    # end of tokens
    validate_and_continue(driver)
