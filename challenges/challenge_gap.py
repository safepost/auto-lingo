import logging

from selenium.webdriver.common.by import By

from challenges.utilities import get_sentence_in_hint_token, check_if_solution_in_db, validate_and_continue, \
    insert_solution_into_db, solve_simple_challenge


def challenge_gap(driver, db):
    solve_simple_challenge(driver, db, "gap")
