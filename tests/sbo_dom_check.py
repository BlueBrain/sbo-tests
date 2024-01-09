"""DOM checker for portal pages.

"""
import time

# pylint: disable=R0913

import pytest

from tests.utils import check_url, load_test_data, wait_for_element, login, logger
import seleniumbase


@pytest.mark.parametrize("path,elements", load_test_data())
def test_sbo(sb, path, elements):
    """Runs the tests for the SSCX dom checks."""

    resource = 'https://bbp.epfl.ch'
    url = f'{resource}{path}'
    logger.info(f'Checking {url}')
    login(sb)
    check_url(sb, url, elements)


def test_open_brain_factory(sb):
    """
    Login
    Go to Brain Factory
    Go to a reference config
    Check whether the side menu loads
    Check whether these buttons load:
      * Cell Composition
      * Cell Model Assignment
      * Connectome Definition
      * Connection Model Assignment
      * Interactive
      * Configuration
      * Build & Simulate
    """
    login(sb)

    logger.info('Selecting a brain model')
    logger.info('Opening Build menu')
    build_menu_item = "//h3[text()='Build']"
    wait_for_element(sb, build_menu_item)
    sb.find_element(build_menu_item, by='xpath').click()

    browse_brain_models_item = "//h2[text()='Browse brain models']"
    wait_for_element(sb, browse_brain_models_item)
    sb.find_element(browse_brain_models_item, by='xpath').click()

    found_config = False
    config = 'Release 23.01'
    config_element = f"//a[text()='{config}']"
    while not found_config:
        try:
            wait_for_element(sb, config_element)
            found_config = True
        except seleniumbase.common.exceptions.NoSuchElementException:
            logger.info("Maybe on the next page")
            next_page_button = "//button[@title='Go to Next Page']"
            wait_for_element(sb, next_page_button)
            sb.find_element(next_page_button, by='xpath').click()

    logger.info(f"Found config {config}")
    sb.find_element(config_element, by='xpath').click()

    title_xpaths = ['//span[text()="Brain region"]', '//span[text()="Basic Cell Groups and '
                                                     'Regions"]']
    for title_xpath in title_xpaths:
        logger.info('Checking for %s title', title_xpath)
        wait_for_element(sb, title_xpath, timeout=15)

    top_nav = '//button[@type="button" and @aria-haspopup="menu"]//div[contains(text(), ' \
              '"Cell composition")]'
    wait_for_element(sb, top_nav).click()

    menu_navigation_items = ['//div[@role="menu"]//div[contains(text(),"Cell composition")]',
                             '//div[@role="menu"]//div[contains(text(),"Cell model assignment")]',
                             '//div[@role="menu"]//div[contains(text(),"Connectome definition")]',
                             '//div[@role="menu"]//div[contains(text(),"Connectome model '
                             'assignment")]'
                             ]
    for nav_item in menu_navigation_items:
        logger.info('Checking for %s menu navigation items', nav_item)
        wait_for_element(sb, nav_item, timeout=1)


    # buttons = [
    #     '//button[text()="Interactive"]',
    #     '//button[text()="Configuration"]',
    # ]
    # for button in buttons:
    #     logger.info('Checking button %s', button)
    #     button_wait = wait_for_element(sb, button)
    #
    logger.info('Checking Build & Simulate button')
    wait_for_element(sb, '//button[text()="Build & Simulate"]')
