import logging
import sys, os, time, json, argparse, random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.chrome.service import Service as ChromeService

from challenges.challenge_assist import challenge_assist
from challenges.challenge_dialogue_readcomp import challenge_dialogue_readcomp
from challenges.challenge_form import challenge_form
from challenges.challenge_gap import challenge_gap
from challenges.challenge_judge import challenge_judge
from challenges.challenge_match import challenge_match
from challenges.challenge_name import challenge_name
from challenges.challenge_reverse_translation import challenge_reverse_translation
from challenges.challenge_select import challenge_select
from challenges.challenge_speak_listen import challenge_speak_listen
from challenges.challenge_tap import challenge_tap, challenge_tap_complete
from challenges.challenge_translate import challenge_translate
import logging
import sqlite3

from challenges.utilities import wait_element

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
# Disabling selenium logging
logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
logger.setLevel(logging.WARNING)


def set_chrome_options(chrome_options):
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    if settings['incognito']:
        chrome_options.add_argument("--incognito")

    if settings['mute_audio']:
        chrome_options.add_argument("--mute-audio")

    if settings['maximize_window']:
        chrome_options.add_argument("start-maximized")

    if settings['headless']:
        chrome_options.add_argument("--headless")


def exit(message=""):
    if message == "":
        message = "Oops! Something went wrong."

    print(message)
    driver.quit()
    sys.exit()


def get_settings():
    settings = {}

    try:
        path = os.path.dirname(__file__)
        with open(os.path.join(path, 'settings.json')) as json_f:
            settings = json.load(json_f)
    except:
        print("Failed to import settings from settings.json.")
        sys.exit()

    if settings['deviation'] > settings['antifarm_sleep'] and settings['antifarm_sleep'] != 0:
        print("deviation cannot be larger than antifarm_sleep time")
        sys.exit()

    if settings['deviation'] < 0:
        print("deviation cannot be negative")
        sys.exit()

    return settings


def get_credentials():
    try:
        path = os.path.dirname(__file__)
        with open(os.path.join(path, 'credentials.json')) as json_file:
            creds = json.load(json_file)

        login = creds['login']
        password = creds['password']
    except:
        return "", ""

    return login, password


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stories",
                        help="stories mode", action="store_true")
    parser.add_argument("-l", "--learn", help="learn mode",
                        action="store_true")
    parser.add_argument("-k", "--mistakes", help="Mistakes mode",
                        action="store_true")
    parser.add_argument("-i", "--incognito",
                        help="incognito browser mode", action="store_true")
    parser.add_argument(
        "-m", "--mute", help="mute browser audio", action="store_true")
    parser.add_argument(
        "-a", "--autologin", help="login to duolingo automatically", action="store_true")

    args = parser.parse_args()

    if args.incognito:
        settings['incognito'] = True

    if args.mute:
        settings['mute_audio'] = True

    if args.autologin:
        settings['auto_login'] = True

    # set default mode to stories
    if not args.learn and not args.stories and not args.mistakes:
        args.stories = True

    return args


def log_in(login, password):
    if settings['auto_login'] and login != "" and password != "":
        logging.debug("Auto login mode")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="web-ui1"]'))
        )
        time.sleep(1)
        email_field.click()
        email_field.clear()
        email_field.send_keys(login)

        password_field = driver.find_element(By.XPATH,
                                             '//input[@data-test="password-input"]')
        password_field.click()
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(0.3)
        login_button = driver.find_element(By.XPATH,
                                           '//button[@data-test="register-button"]')
        login_button.click()

    try:
        wait = WebDriverWait(driver, 25)
        wait.until(lambda driver: driver.current_url ==
                                  "https://www.duolingo.com/learn")

        print('Loggin in')

    except WebDriverException:
        exit("Timed out. Please login to Duolingo in time.")


# this function is dedicated to all imbecils who put "Correct solution:" inside the solution itself

def anti_imbecil_check(solution):
    return len(solution) > 17 and solution[0:17] == "Correct solution:"


def task_tokens(tokens):
    # I think this is where the solving happens
    done_list = []

    for i in range(len(tokens)):
        if i in done_list:
            continue

        for j in range(len(tokens)):
            if j in done_list or i == j:
                continue

            tokens[i].click()
            tokens[j].click()

            # check if we found a pair
            classes = tokens[i].get_attribute('class')
            if '_3alTu' in classes:
                done_list.append(i)
                done_list.append(j)
                break


def task_options(options):
    for option in options:
        try:
            if option.get_attribute('data-test') == 'challenge-tap-token':
                challenge_match()
            else:
                option.click()
        except WebDriverException:
            pass


def complete_story():
    start_story = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, '//button[@data-test="story-start"]'))
    )
    start_story.click()

    task_list = ['//span[@data-test="stories-phrase"]',
                 '//button[@data-test="stories-choice"]',
                 '//div[@data-test="stories-selectable-phrase"]',
                 '//button[@data-test="challenge-tap-token"]',
                 '//button[@data-test="stories-token"]',
                 ]
    done_tokens = False

    while True:
        # try to click next button
        try:
            next = driver.find_element(By.XPATH,
                                       '//button[@data-test="stories-player-continue"]')
            next.click()
        except WebDriverException:
            pass

        try:
            story_done = driver.find_element(By.XPATH,
                                             '//button[@data-test="stories-player-done"]')
            break
        except WebDriverException:
            pass

        try:
            blank_item = driver.find_element(
                By.XPATH, '//div[@class="_2fX2D"]')
            break
        except WebDriverException:
            pass

        if not done_tokens:
            # try to do any task
            for task in task_list:
                options = driver.find_elements(By.XPATH, task)
                # if did not find that task
                if len(options) == 0:
                    continue

                if task == task_list[-1]:
                    task_tokens(options)
                    done_tokens = True
                else:
                    task_options(options)

                break

    # close story tab and switch to main tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def complete_skill(driver, db, possible_skip_to_lesson=False):
    logging.debug("Entering complete skill")
    if possible_skip_to_lesson:
        time.sleep(2)
        try:
            skip_to_lesson = driver.find_element(By.XPATH,
                                                 '//button[@class="_3o5OF _2q8ZQ t5wFJ yTpGk _2RTMn _3yAjN"]')
            skip_to_lesson.click()
        except WebDriverException:
            pass

    # wait for site to initialize
    try:
        skip = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-test="player-skip"]'))
        )
    except WebDriverException:
        pass

    skill_completed = False

    while not skill_completed:
        logging.debug("Starting skill resolution")
        while True:
            try:
                no_thanks = driver.find_element(By.XPATH,
                                                '//button[@data-test="no-thanks-to-plus"]')
                skill_completed = True
                break
            except WebDriverException:
                pass


            # end of session => session-complete-slide

            try:
                challenge = wait_element(driver,
                                         '//div[contains(@data-test,"challenge")]', 2)
                chall_type = challenge.get_attribute("data-test")
                print(f"Got challenge ! {chall_type}")

                if "challenge-match" in chall_type:
                    challenge_match(driver, db)
                elif any(_s in chall_type for _s in ["speak", "listen", "selectTranscription"]):
                    logging.debug("Detected Speak / Listen challenge")
                    challenge_speak_listen(driver)
                elif "challenge-form" in chall_type:
                    challenge_form(driver, db)
                elif "challenge-judge" in chall_type:
                    challenge_judge(driver, db)
                elif "challenge-translate" in chall_type:
                    logging.debug("Detected challenge translate !")
                    challenge_translate(driver, db)
                elif "completeReverseTranslation" in chall_type:
                    challenge_reverse_translation(driver, db)
                elif "challenge-name" in chall_type:
                    challenge_name(driver, db)
                elif "challenge-select" in chall_type:
                    challenge_select(driver, db)
                elif "challenge-assist" in chall_type:
                    challenge_assist(driver, db)
                elif "challenge-tapComplete" in chall_type:
                    challenge_tap_complete(driver, db)
                elif "challenge-dialogue" in chall_type:
                    challenge_dialogue_readcomp(driver, db, True)
                elif "challenge-readComprehension" in chall_type:
                    challenge_dialogue_readcomp(driver, db, False)
                elif "challenge-gapFill" in chall_type:
                    challenge_gap(driver, db)
                elif "partialReverseTranslate" in chall_type:
                    challenge_translate(driver, db, "partialReverseTranslate")
                else:
                    logging.info(f"New challenge detected : {chall_type}")
                    logging.info("Need to implement")

            except StaleElementReferenceException:
                logging.debug("Element no longer present in page")
            except Exception as err:
                # Challenge not found => Clic in Continue button
                try:
                    continue_button = wait_element(driver, '//button[@data-test="player-next"]', 1)
                    continue_button.click()
                except:
                    print("Continue not found")

                # Go legendardy check
                try:
                    dont_go_legendary = wait_element(driver, '//span[@class="_1fHYG"]', 1)
                    dont_go_legendary.click()
                except:
                    print("Don't go legendary")

                # close-button
                try:
                    close_button = wait_element(driver, '//div[@data-test="close-button"]', 1)
                    close_button.click()
                except:
                    print("Close button")

                print(type(err))
                print(err)



            if driver.current_url == "https://www.duolingo.com/learn":
                logging.debug("Detecting end of lesson")
                skill_completed = True
                break

            logging.debug("Rest between cycle")
            time.sleep(0.4)
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-speak"]')
            #     print("Detected speak listen")
            #
            #     challenge_speak_listen(driver)
            # except WebDriverException:
            #     pass

            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-listen"]')
            #     print("Detected speak listen")
            #
            #     challenge_speak_listen(driver)
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-listenTap"]')
            #     print("Detected speak listen")
            #
            #     challenge_speak_listen(driver)
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-selectTranscription"]')
            #     print("Detected speak listen")
            #
            #     challenge_speak_listen(driver)
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-form"]')
            #     print("Detected challenge form")
            #
            #     challenge_form(driver, solutions)
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-judge"]')
            #
            #     print("Detected challenge judge")
            #
            #     challenge_judge(driver, solutions)
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-translate"]')
            #     print("Detected challenge translate")
            #     challenge_translate(driver, db)
            # except WebDriverException as err:
            #     pass
            #     # print(f"Exception : {err}")
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-completeReverseTranslation"]')
            #     print("Detected reverse translate")
            #
            #     challenge_reverse_translation(driver, solutions)
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-name"]')
            #     print("Detected challenge name")
            #
            #     challenge_name(driver, solutions)
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-select"]')
            #     print("Detected challenge select")
            #
            #     challenge_select(driver, db)
            # except WebDriverException:
            #     pass
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-assist"]')
            #     print("Detected challenge assist (new => write me please !!)")
            #
            #     challenge_assist(driver, db)
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-tapComplete"]')
            #     print("Detected challenge tap complete")
            #     challenge_tap_complete(driver, db)
            # except WebDriverException:
            #     pass

            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-dialogue"]')
            #     print("Detected challenge dialogue")
            #
            #     challenge_dialogue_readcomp(driver, solutions, True)
            #     # break
            # except WebDriverException:
            #     pass
            #
            # logging.debug("in loop")
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-listenComprehension"]')
            #     print("Detected speak listen")
            #
            #     challenge_speak_listen(driver)
            #     # break
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-readComprehension"]')
            #     print("Detected read comprehension")
            #
            #     challenge_dialogue_readcomp(driver, solutions, False)
            #     # break
            # except WebDriverException:
            #     pass
            #
            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-gapFill"]')
            #     print("Detected gap fill")
            #
            #     challenge_gap(driver, solutions)
            #     # break
            # except WebDriverException:
            #     pass

            # try:
            #     challenge = driver.find_element(By.XPATH,
            #                                     '//div[@data-test="challenge challenge-match"]')
            #     print("Detected challenge match")
            #     challenge_match(driver, db)
            #     # break
            # except WebDriverException:
            #     pass

            # try:
            #     next = driver.find_element(By.XPATH,
            #                                '//button[@data-test="player-next"]')
            #     print("Player next clic")
            #     next.click()
            #     break
            # except WebDriverException:
            #     pass

            # check if we already quit the skill
            # try:
            #     blank_item = driver.find_element(By.XPATH,
            #                                      '//div[@class="_2fX2D"]')
            #     print("Quitting skill ?!")
            #
            #     skill_completed = True
            #     break
            # except WebDriverException:
            #     pass

        time.sleep(0.2)


def stories_bot():
    print("📙 STORIES BOT")

    while True:
        driver.get("https://www.duolingo.com/stories?referrer=web_tab")
        stories = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@class="_2nLk_" and not(@class="_3N2Ph")]//div[@class="X4jDx"]'))
        )

        if len(stories) == 0:
            break

        for story in stories:
            story_display = story.text.splitlines()
            if "+0 XP" in story.text:
                print(f"📖 Skipping {story_display[0]}")
                continue

            print(f"📙 Starting {story_display[0]}")
            driver.execute_script("arguments[0].scrollIntoView();", story)
            story.click()

            read_story = story.find_element(By.XPATH,
                                            './/a[@data-test="story-start-button"]')
            story_url = read_story.get_attribute('href')

            driver.execute_script("window.open('" + story_url + "', '_blank')")
            driver.switch_to.window(driver.window_handles[1])

            complete_story()
            if settings['antifarm_sleep'] > 0:
                deviation = random.randint(-settings['deviation'],
                                           settings['deviation'])
                time.sleep(settings['antifarm_sleep'] + deviation)

            print(f"📙 Finishing {story_display[0]}")


def mistakes():
    print("Entering mistakes mode")
    while True:
        driver.get("https://www.duolingo.com/practice-hub/mistakes")
        skills = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="root"]/div[5]/div/div/div/div[2]/div[1]/button/span'))
        )

        # //*[@id="root"]/div[5]/div/div/div/div[2]/div[1]/button

        print("button detected")

        completed_skill = False

        for skill in skills:
            try:
                start_skill = skill.find_element(By.XPATH,
                                                 '//*[@id="root"]/div[5]/div/div/div/div[2]/div[1]/button/span]')
                start_skill.click()
                print("button cliked")
                complete_skill()
                completed_skill = True

                if settings['antifarm_sleep'] > 0:
                    time.sleep(settings['antifarm_sleep'])

                break

            except WebDriverException:
                pass

            # search for g tag with grey circle fill
            # cannot search for skills with level < 5 because some skills cap at level 1
            try:
                g_tag = skill.find_element(by=By.TAG_NAME, value='g')
            except WebDriverException:
                continue

            if 'fill="#e5e5e5"' not in g_tag.get_attribute('innerHTML'):
                continue

            # first check if there is a chance for "Welcome to x!" screen with skip to lesson button
            possible_skip_to_lesson = False

            # if the chosen skill has no crowns, there is a chance an additional screen will pop up
            try:
                zero_level = skill.find_element(By.XPATH,
                                                './/div[@data-test="level-crown"]')
            except WebDriverException:
                possible_skip_to_lesson = True

            # before doing anything with skills, perform a blank click for possible notifications to disappear
            blank_item = driver.find_element(
                By.XPATH, '//div[@class="_2fX2D"]')
            action = ActionChains(driver)
            action.move_to_element(blank_item).click().perform()

            time.sleep(0.5)

            # navigate to chosen skill
            action = ActionChains(driver)
            action.move_to_element(skill).perform()

            time.sleep(0.5)

            skill.click()

            time.sleep(0.5)

            found = True
            try:
                start_skill = skill.find_element(By.XPATH,
                                                 '//a[@data-test="start-button"]')
            except WebDriverException:
                found = False
            if not found:
                start_skill = skill.find_element(By.XPATH,
                                                 '//button[@data-test="start-button"]')

            action = ActionChains(driver)
            action.move_to_element(start_skill).click().perform()

            complete_skill(possible_skip_to_lesson)

            completed_skill = True

            if settings['antifarm_sleep'] > 0:
                deviation = random.randint(-settings['deviation'],
                                           settings['deviation'])
                time.sleep(settings['antifarm_sleep'] + deviation)

            break

        if not completed_skill:
            break


def learn_bot(driver, db):
    # //*[@id="root"]/div[5]/div/div/div[2]/section[3]/div/div[4]/div/div/button
    # Starting point to put on DB or in conf (or both)
    unit = 3
    level = 1
    while True:
        lesson_url = f"https://www.duolingo.com/lesson/unit/{unit}/level/{level}"
        time.sleep(1)
        driver.get(lesson_url)
        if driver.current_url != lesson_url:
            unit += 1
            level = 1
            continue
        complete_skill(driver, db)
        level += 1

        # driver.get("https://www.duolingo.com/learn")
        # skills = WebDriverWait(driver, 20).until(
        #     EC.presence_of_all_elements_located(
        #         # (By.XPATH, '//button[@data-test="skill-path-level-0 skill-path-level-skill"]'))
        #         # (By.XPATH, '//button[@data-test="skill"]'))
        #         (By.XPATH, '//button[contains(@data-test,"skill-path-level")]'))
        #     # (By.XPATH, '//div[@data-test]'))
        # )
        # print("Detected skills")
        # print(skills)
        # completed_skill = False
        #
        # for skill in skills:
        #     print(f"Current skill ID {skill.id}")
        #     with open(f"screens/{skill.id}.png", "wb") as e:
        #         e.write(skill.screenshot_as_png)
        #     print(f"{skill.tag_name} {skill.get_attribute('data-test')}")
        #     # skill.click()
        #     try:
        #         start_skill = skill.find_element(By.XPATH,
        #                                          '//button[contains(@data-test,"skill-path-level-0")]')
        #         print("Clicking on skill")
        #         start_skill.click()
        #         print("Button clicked !")
        #         complete_skill()
        #         completed_skill = True
        #
        #         if settings['antifarm_sleep'] > 0:
        #             time.sleep(settings['antifarm_sleep'])
        #
        #         break
        #
        #     except WebDriverException as err:
        #         print(err)
        #         pass
        #
        #     # search for g tag with grey circle fill
        #     # cannot search for skills with level < 5 because some skills cap at level 1
        #     try:
        #         g_tag = skill.find_element(by=By.TAG_NAME, value='g')
        #     except WebDriverException:
        #         continue
        #
        #     if 'fill="#e5e5e5"' not in g_tag.get_attribute('innerHTML'):
        #         continue
        #
        #     # first check if there is a chance for "Welcome to x!" screen with skip to lesson button
        #     possible_skip_to_lesson = False
        #
        #     # if the chosen skill has no crowns, there is a chance an additional screen will pop up
        #     try:
        #         zero_level = skill.find_element(By.XPATH,
        #                                         './/div[@data-test="level-crown"]')
        #     except WebDriverException:
        #         possible_skip_to_lesson = True
        #
        #     # before doing anything with skills, perform a blank click for possible notifications to disappear
        #     blank_item = driver.find_element(
        #         By.XPATH, '//div[@class="_2fX2D"]')
        #     action = ActionChains(driver)
        #     action.move_to_element(blank_item).click().perform()
        #
        #     time.sleep(0.5)
        #
        #     # navigate to chosen skill
        #     action = ActionChains(driver)
        #     action.move_to_element(skill).perform()
        #
        #     time.sleep(0.5)
        #
        #     skill.click()
        #
        #     time.sleep(0.5)
        #
        #     found = True
        #     try:
        #         start_skill = skill.find_element(By.XPATH,
        #                                          '//a[@data-test="start-button"]')
        #     except WebDriverException:
        #         found = False
        #     if not found:
        #         start_skill = skill.find_element(By.XPATH,
        #                                          '//button[@data-test="start-button"]')
        #
        #     action = ActionChains(driver)
        #     action.move_to_element(start_skill).click().perform()
        #
        #     complete_skill(possible_skip_to_lesson)
        #
        #     completed_skill = True
        #
        #     if settings['antifarm_sleep'] > 0:
        #         deviation = random.randint(-settings['deviation'],
        #                                    settings['deviation'])
        #         time.sleep(settings['antifarm_sleep'] + deviation)
        #
        #     break
        #
        # if not completed_skill:
        #     break


def main():
    print("🏁 Starting out")

    global dictionary
    dictionary = {}

    db = sqlite3.connect("database/solutions.db")

    with open("database/initialization.sql", 'r') as sql_file:
        sql_script = sql_file.read()

    cursor = db.cursor()
    try:
        cursor.executescript(sql_script)
        db.commit()
    except sqlite3.OperationalError:
        pass


    global settings
    settings = get_settings()

    login, password = get_credentials()

    args = parse_arguments()

    chrome_options = Options()
    set_chrome_options(chrome_options)

    global driver

    service = ChromeService(executable_path=settings['chromedriver_path'])

    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.duolingo.com/?isLoggingIn=true")
    # driver.get("https://www.duolingo.com/?isLoggingIn=true")

    wait = WebDriverWait(driver, 20)

    try:
        have_account = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-test="have-account"]'))
        )
        cookies = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
        )
        cookies.click()
        have_account.click()
    except WebDriverException as e:
        exit(e)

    log_in(login, password)
    print(args)

    if args.mistakes:
        mistakes()

    if args.learn:
        learn_bot(driver, db)

    if args.stories:
        stories_bot()

    exit("Auto-lingo finished.")


if __name__ == "__main__":
    main()
