"""DOM checker for portal pages.

The code will load random pages and checks for expected DOM elements.
"""
# pylint: disable=R0913

import time
import json
import random
from io import BytesIO
from PIL import Image

import pytest
from selenium.common import exceptions


# TODO: actually add output
LOG_OUTPUT = "page_dom_check.log"


def make_full_screenshot(driver, savename):
    """Performs a full screenshot of the entire page.
    Taken from https://gist.github.com/fabtho/13e4a2e7cfbfde671b8fa81bbe9359fb
    """
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


def find_element(driver, method, name, operator=None, count=None):
    """Returns True, if elements exists in webpage, False else.

    Args:
        method (string): Name of the selenium method to find an element.
        name (string): Name of the element to find.
    """
    try:
        if count:
            elements = driver.find_elements(name, by=method)
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
            driver.find_element(name, by=method, timeout=1.0)
        return True
    except exceptions.NoSuchElementException:
        return False


def write_errors(filename, site, url, errors):
    """Adds a new entry to the output file when an expected ID is not found.

    Args:
        filename (string): Output filename.
        site (string): The portal site the error has been found on.
        url (string): The exact URL on which the error has been found.
        errors (list): The element(s) that were not found.
    """
    with open(filename, "a+") as fileout:
        fileout.write(f"{site} -> {url}: {errors}\n")


def check_url(driver, url, elements=None):
    """Function to check a single URL."""

    time0 = time.time()

    def debug(txt):
        time_now = time.time() - time0
        print(f"    {time_now:.1f} - {txt}")

    # Call selenium method to open URL
    debug(f"Opening URL {url}")
    driver.open(url)

    if elements:
        for info in elements:
            if len(info) == 2:
                method, element = info
                count = None
                operator = None
            elif len(info) == 4:
                method, element, operator, count = info

            found = find_element(driver, method, element, operator, count)
            if not found:
                raise RuntimeError(f'Element {element} not found')

    # Close the current driver
    driver.driver.close()
    driver.driver.quit()


def load_test_data():
    with open('sbo-dom-checks.json', 'r') as fp:
        test_data = json.load(fp)
    return test_data


@pytest.mark.parametrize("path,elements", load_test_data())
def test_sbo(selbase, path, elements):
    """Runs the tests for the SSCX dom checks."""

    resource = 'https://bbp.epfl.ch'
    url = f'{resource}{path}'
    print(f"Checking {url} with elements {elements}")
    check_url(selbase, url, elements)
