from holmium.core.logger import log
from holmium.core.testcase import HolmiumTestCase, browser_mapping, capabilities, Screenshot
from holmium.core.pageobject import Locators, PageObject, PageElement, PageElements
from holmium.core.pageobject import PageElementMap
from holmium.core.pageobject import ExtendedWebElement
from holmium.core.pageobject import safe_lambda
from holmium.core.decorators import repeat
from holmium.core.noseplugin import HolmiumNose
screenshot_wrapper = Screenshot()
ExtendedWebElement.register_callback( screenshot_wrapper.trigger )

