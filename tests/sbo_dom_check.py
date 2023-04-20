"""DOM checker for portal pages.

"""
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

    menu_items = [
        ('Cell composition', f'/mmb-beta/build/cell-composition/interactive?brainModelConfigId={refConfigId}'),
        ('Cell model assignment', f'/mmb-beta/build/cell-model-assignment?brainModelConfigId={refConfigId}'),
        ('Connectome definition', f'/mmb-beta/build/connectome-definition/configuration?brainModelConfigId={refConfigId}'),
        ('Connection model assignment', f'/mmb-beta/build/connectome-model-assignment?brainModelConfigId={refConfigId}'),
    ]
    for menu_item in menu_items:
        logger.info('Checking menu item: %s', menu_item[0])
        menu_xpath = f'//div[@class="flex"]/a[text()="{menu_item[0]}" and @href="{menu_item[1]}"]'
        wait_for_element(sb, menu_xpath)

    logger.info('Checking Build & Simulate button')
    wait_for_element(sb, '//button[text()="Build & Simulate"]')

    buttons = [
        ("Interactive", f"/mmb-beta/build/cell-composition/interactive?brainModelConfigId={refConfigId}"),
        ("Configuration", f"/mmb-beta/build/cell-composition/configuration?brainModelConfigId={refConfigId}")
    ]
    for button in buttons:
        logger.info('Checking button %s', button[0])
        button_xpath = f'//div/div/div/a[text()="{button[0]}" and @href="{button[1]}"]'
        wait_for_element(sb, button_xpath)
