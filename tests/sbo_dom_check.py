"""DOM checker for portal pages.

"""
import time

# pylint: disable=R0913

from furl import furl
import pytest

from tests.utils import check_url, load_test_data, wait_for_element, login, logger
from selenium.common.exceptions import NoSuchElementException


@pytest.mark.parametrize("path,elements", load_test_data())
def test_sbo(sb, path, elements):
    """Runs the tests for the SSCX dom checks."""

    resource = 'https://bbp.epfl.ch'
    url = f'{resource}{path}'
    logger.info(f'Checking %s', url)
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

    logger.info('Opening brain factory')
    brain_factory_link = '//a[@href="/mmb-beta/build/load-brain-config"]'
    wait_for_element(sb, brain_factory_link)
    sb.find_element(brain_factory_link, by='xpath').click()

    config = 'Release 23.01'
    logger.info('Opening config %s', config)
    config_link = f'//div[text()="{config}"]/../..'
    wait_for_element(sb, config_link)
    config_link = sb.find_element(config_link, by='xpath')
    f = furl(config_link.get_attribute("href"))
    logger.debug('Url for config: %s', f.tostr())
    logger.debug('Querystring: %s', str(f.query))
    refConfigId = str(f.query).split('=')[1]
    logger.info('Config ID: %s', refConfigId)
    config_link.click()

    title_xpaths = ['//span[text()="Brain region"]', '//span[text()="Basic cell groups and regions"]']
    for title_xpath in title_xpaths:
        logger.info('Checking for %s title', title_xpath)
        wait_for_element(sb, title_xpath, timeout=15)

    # top_nav = f'//button[@type="button" and @aria-haspopup="menu"]/div[@class="flex flex-row gap-x-3"]'
    # top_nav = f'//div[@class="flex min-w-[290px] h-full"]//div[contains(text(), "Cell composition")]'
    top_nav = f'//button[@type="button" and @aria-haspopup="menu"]//div[contains(text(), "Cell composition")]'
    wait_for_element(sb, top_nav).click()

    menu_navigation_items = ['//div[@role="menu"]//div[contains(text(),"Cell composition")]',
                             '//div[@role="menu"]//div[contains(text(),"Cell composition")]',
                             '//div[@role="menu"]//div[contains(text(),"Connectome definition")]',
                             '//div[@role="menu"]//div[contains(text(),"Connection model assignment")]'
                             ]
    for nav_item in menu_navigation_items:
        logger.info('Checking for %s menu navigation items', nav_item)
        wait_for_element(sb, nav_item, timeout=5)

    logger.info('Checking Build & Simulate button')
    wait_for_element(sb, '//button[text()="Build & Simulate"]')


    # second_nav_menu = f'//div[@class="flex justify-end min-w-[290px] h-full"]/button[@type="button"]'
    # second_nav_menu = f'//button[@type="button"]/div[contains(text(), "Interactive")]'
    # wait_for_element(sb, second_nav_menu, timeout=2).click()

    # time.sleep(20)
    # buttons = [
    #     '//button[text()="Interactive"]',
    #     '//button[text()="Configuration"]'
    # ]
    # for button in buttons:
    #     logger.info('Checking button %s', button)
    #     wait_for_element(sb, button)

#
