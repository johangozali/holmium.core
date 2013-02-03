from holmium.core.logger import log
from holmium.core.testcase import HolmiumTestCase, browser_mapping, capabilities, Screenshot
from holmium.core.pageobject import Locators, PageObject, PageElement, PageElements
from holmium.core.pageobject import PageElementMap
from holmium.core.pageobject import TrackedWebElement
from holmium.core.decorators import repeat
from holmium.core.noseplugin import HolmiumNose
screenshot_wrapper = Screenshot()
TrackedWebElement.register_callback( screenshot_wrapper.trigger )

