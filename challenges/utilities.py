import logging
import re
import sqlite3

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, expected_conditions

def remove_useless_punct(word):
    for a in ".,!?;":
        word = word.replace(a, "")

    return word

    # solution = word.replace(".", "").replace(",", "").replace("!", "").replace("?", "").replace(";", "").lower()


def remove_punct(word):
    return re.sub(r'[^\w\s]', '', word)

def remove_specials(word):
    return re.sub("[^a-zA-Z ]", "", word)

def remove_punct_smart(sentence: str):
    # decoupage de la phrase
    unwanted = "?!."

    _sentence = sentence.replace("-", " ")
    _sentence = _sentence.replace("'", "' ")
    _sentence = _sentence.strip(unwanted)
    _s_list = _sentence.split(" ")
    _final = [_s for _s in _s_list if _s != '']

    return _final


def insert_solution_into_db(db: sqlite3.Connection, db_name: str, sentence, solution):
    _cur = db.cursor()
    logging.debug(f"INSERT INTO {db_name} VALUES ('{sentence}', '{solution}')")
    # _cur.execute(f"INSERT INTO {db_name} VALUES ('{sentence}', '{solution}')")
    _cur.execute(f"INSERT INTO {db_name} VALUES (?, ?)", (sentence, solution))
    db.commit()


def check_if_solution_in_db(db: sqlite3.Connection, db_name, sentence: str):
    _cur = db.cursor()
    logging.debug(f"SELECT solution FROM {db_name} WHERE sentence = '{sentence}'")
    res = _cur.execute(f"SELECT solution FROM {db_name} WHERE sentence = ?", [sentence])
    solution = res.fetchone()
    logging.debug(solution)
    if solution is not None:
        return solution[0]
    else:
        return False

def validate_and_continue(driver):
    logging.debug("Finding validation button")
    validation_button = driver.find_element(By.XPATH, '//button[@data-test="player-next"]')
    validation_button.click()
    logging.debug("Clicked on validation button")
    continue_button = driver.find_element(By.XPATH, '//button[@data-test="player-next"]')
    continue_button.click()


def contains(driver, elem, attribute, value):
    """
    elem => button / span / div ...
    attribute => data-test / class ...
    elem => _1fc3
    """
    xpath = f'//{elem}[contains(@{attribute},"{value}")]'

    logging.debug(xpath)
    return driver.find_element(By.XPATH, xpath)


if __name__ == "__main__":
    driver = "tutu"
    contains(driver, "button", "data-test", "skill-path-level")

    exit(0)
    lol = "tutu"
    print(lol.split("//"))
    exit(0)

    challenge: list = ['my', 'family', 'your', 'family']
    answer = "this is my family is this your family"
    answer_list: list = answer.split(" ")

    sublist_size = len(challenge)
    print(sublist_size)
    print(answer_list[0:sublist_size])
    k = 0
    for i in range(1, len(challenge)):
        if answer[k:sublist_size] == challenge:
            print("equivalent list")

    exit(0)

    test_me = "Est-ce que c'est ta cousine Anna ?"
    returned = remove_punct_smart(test_me)
    print(returned)

    tap_token = ['thé', 'oui', 'frère', 'petit', 'café', 'tea', 'yes', 'coffee', 'brother', 'small']
    tap_token1 = tap_token[:5]
    tap_token2 = tap_token[5:]
    print(tap_token1)
    print(tap_token2)


def wait_element(driver, xpath, wait_time=5):
    element = WebDriverWait(driver, wait_time).until(expected_conditions.any_of(
        EC.presence_of_element_located((By.XPATH, xpath)),

    ))

    return element

def get_sentence_in_hint_token(driver):
    sentence_token = driver.find_elements(By.XPATH, '//div[@data-test="hint-token"]')
    logging.debug(len(sentence_token))
    _sentence_list = [_s.get_attribute("aria-label") for _s in sentence_token]
    logging.debug(_sentence_list)
    return _sentence_list


def solve_simple_challenge(driver, db, table_name):
    sentence_list = get_sentence_in_hint_token(driver)
    sentence = " ".join(sentence_list)
    print(f"Detected Sentence : {sentence}")

    existing_solution = check_if_solution_in_db(db, table_name, sentence)

    if existing_solution:
        logging.debug(f"Existing solution found: {existing_solution}")
        choices = driver.find_elements(By.XPATH,
                                       '//span[@data-test="challenge-judge-text"]')

        logging.debug([c.text for c in choices])
        for choice in choices:
            if choice.text == existing_solution:
                choice.click()
                logging.debug(f"Clicked on {choice.text}")
                break

        validate_and_continue(driver)
        print("clicked !")
        # return True

    else:
        skip = driver.find_element(By.XPATH,
                                   '//button[@data-test="player-skip"]')
        skip.click()
        solution = driver.find_element(By.XPATH,
                                       '//div[contains(@class,"_1UqAr")]').text
        logging.debug(f"Adding Sentence {sentence} with solution {solution}")
        insert_solution_into_db(db, table_name, sentence, solution)