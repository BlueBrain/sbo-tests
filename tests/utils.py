import json
import logging
import os
import time

from io import BytesIO
from PIL import Image
from selenium.common import exceptions, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


logger = logging.getLogger()
fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh = logging.FileHandler("page_dom_check.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(fmt)
logger.addHandler(fh)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(fmt)
logger.addHandler(sh)
logger.setLevel(logging.DEBUG)


def make_full_screenshot(driver, savename):
    """Performs a full screenshot of the entire page.
    Taken from https://gist.github.com/fabtho/13e4a2e7cfbfde671b8fa81bbe9359fb
    """
    logger.debug('Making full-page screenshot')
    # initiate value
    img_list = []  # to store image fragment
    offset = 0  # where to start

    # js to get height of the window
    try:
        height = driver.execute_script(
            "return Math.max("
            "document.documentElement.clientHeight, window.innerHeight);"
        )
    except exceptions.WebDriverException:
        return

    # js to get the maximum scroll height
    # Ref--> https://stackoverflow.com/questions/17688595/
    #        finding-the-maximum-scroll-position-of-a-page
    max_window_height = driver.execute_script(
        "return Math.max("
        "document.body.scrollHeight, "
        "document.body.offsetHeight, "
        "document.documentElement.clientHeight, "
        "document.documentElement.scrollHeight, "
        "document.documentElement.offsetHeight);"
    )

    # looping from top to bottom, append to img list
    # Ref--> https://gist.github.com/fabtho/13e4a2e7cfbfde671b8fa81bbe9359fb
    header_height = 0
    while offset < max_window_height:
        driver.execute_script(f"window.scrollTo(0, {offset});")
        time.sleep(1)

        # get the screenshot of the current window
        img = Image.open(BytesIO((driver.driver.get_screenshot_as_png())))
        img_list.append(img)
        offset += height - header_height

    # Stitch image into one, set up the full screen frame
    img_frame_height = sum([img_frag.size[1] for img_frag in img_list])
    img_frame = Image.new("RGB", (img_list[0].size[0], img_frame_height))

    offset = 0  # offset used to create the snapshots
    img_loc = 0  # offset used to create the final image
    for img_frag in img_list:
        # image fragment must be cropped in case the page is a jupyter notebook;
        # also make sure the last image fragment gets added correctly to avoid overlap.
        offset1 = offset + height
        if offset1 > max_window_height:
            top_offset = offset + height - max_window_height
            box = (0, top_offset, img_frag.size[0], img_frag.size[1])
        else:
            box = (0, header_height, img_frag.size[0], img_frag.size[1])
        img_frame.paste(img_frag.crop(box), (0, img_loc))
        img_loc += img_frag.size[1] - header_height
        offset += height - header_height

    # Save the final image
    img_frame.save(savename)


def wait_for_element(selbase, element, find_by='xpath', timeout=10):
    """
    Wait for an element to appear
    Args:
        selbase (selbase): the selenium base object
        element (string): the element to find
        find_by (string): how to locate the element (defaults to xpath)
        timeout (int): how long, in seconds, to wait (defaults to 10)
    """
    logger.debug('Waiting for %s by %s for up to %s seconds', element, find_by, timeout)
    found_element = WebDriverWait(selbase, timeout=timeout).until(
        lambda d: d.find_element(element, by=find_by),
        message=f'Timeout waiting for {element} on {selbase.get_current_url()}')
    logger.debug('Found element %s', element)

    return found_element


def wait_for_elements(selbase, element, find_by='xpath', timeout=10):
    """
    Wait for an element to appear
    Args:
        selbase (selbase): the selenium base object
        element (string): the element to find
        find_by (string): how to locate the element (defaults to xpath)
        timeout (int): how long, in seconds, to wait (defaults to 10)
    """
    logger.debug('Waiting for %s by %s for up to %s seconds', element, find_by, timeout)
    elements = WebDriverWait(selbase, timeout=timeout).until(
        lambda d: d.find_elements(element, by=find_by),
        message=f'Timeout waiting for {element} on {selbase.get_current_url()}')

    return elements


def element_exists(driver, method, name, operator=None, count=None):
    """Returns True, if elements exists in webpage, False else.

    Args:
        driver (selbase): the selenium base object
        method (string): Name of the selenium method to find an element.
        name (string): Name of the element to find.
        operator (string): optionally, how to compare count to the amount of elements found
        count (int): how many should be found (at most, at least, ... - see operator)
    """
    logger.debug('Checking whether %s exists', name)
    try:
        if count:
            elements = wait_for_elements(driver, name, find_by=method)
            if operator == '=' and len(elements) != count:
                return False
            elif operator == '>' and len(elements) <= count:
                return False
            elif operator == '<' and len(elements) >= count:
                return False
            elif operator == '>=' and len(elements) < count:
                return False
            elif operator == '<=' and len(elements) > count:
                return False
        else:
            wait_for_element(driver, name, find_by=method)
        return True
    except exceptions.NoSuchElementException:
        return False


def check_url(driver, url, elements=None):
    """Function to check a single URL."""

    time0 = time.time()

    # Call selenium method to open URL
    logger.debug(f"Opening URL {url}")
    try:
        driver.open(url)
    except:  # no Exception type as the expected one does not seem to get caught
        logger.critical(f"Issue while opening {url} - retrying once.")
        driver.open(url)

    if elements:
        for info in elements:
            if len(info) == 2:
                method, element = info
                count = None
                operator = None
            elif len(info) == 4:
                method, element, operator, count = info

            logger.info('Checking element %s', element)
            found = element_exists(driver, method, element, operator, count)
            if not found:
                raise RuntimeError(f'Element {element} not found')

    # Close the current driver
    driver.driver.close()
    driver.driver.quit()


def load_test_data():
    with open('data/sbo-dom-checks.json', 'r') as fp:
        test_data = json.load(fp)
    return test_data


def get_credentials():
    """
    Retrieve the credentials to use.
    First checks for MMB_LOGIN and MMB_PASSWORD variables in the environment
    (e.g. for gitlab use).
    If both aren't present, checks for data/credentials.json
    (e.g. for development use).
    The json file is very simple:
    {
        "username": "<username>",
        "password": "<password>"
    }
    """
    if 'MMB_LOGIN' in os.environ and 'MMB_PASSWORD' in os.environ:
        credentials = {'username': os.environ['MMB_LOGIN'],
                       'password': os.environ['MMB_PASSWORD']}
    else:
        with open('data/credentials.json', 'r') as fp:
            credentials = json.load(fp)

    return credentials


def login(selbase):
    """Logs in"""

    resource = 'https://bbp.epfl.ch/mmb-beta'
    selbase.open(resource)
    try:
        logger.info('Looking for login button')
        login_button = selbase.find_element('//button[text()="Login"]', by='xpath')
    except NoSuchElementException:
        logger.info('Login button not found - assuming already logged in')
        return
    login_button.click()
    username_field = '//input[@id="username"]'
    password_field = '//input[@id="password"]'
    login = '//input[@id="kc-login"]'
    for element in [username_field, password_field, login]:
        wait_for_element(selbase, element)

    credentials = get_credentials()

    logger.debug('Logging in with user %s', credentials['username'])
    selbase.find_element(username_field, by='xpath').send_keys(
        credentials['username'])
    selbase.find_element(password_field, by='xpath').send_keys(
        credentials['password'])
    selbase.find_element(login, by='xpath').click()

    wait_for_element(selbase, '//button[text()="Logout"]')
