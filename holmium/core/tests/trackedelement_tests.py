import unittest
from  holmium.core import PageObject, PageElement, PageElements,PageElementMap, Locators
import selenium.webdriver
from holmium.core.pageobject import ExtendedWebElement

class TrackedElementTest(unittest.TestCase):
    page_content = """
            <body id="root">
                <div id="simple_id">simple_id</div>
                <div class="simple_class">simple_class</div>
                <div class="simple_xpath"><h3>Simple XPATH</h3></div>
            </body>
        """

    def setUp(self):
        self.driver = selenium.webdriver.PhantomJS()
        self.callback_messages = []
        def cb(*args):
            self.callback_messages.append(args)
        ExtendedWebElement.register_callback(cb)
    def test_callback(self):
        class SimplePage(PageObject):
            elements = { "id": PageElement ( Locators.ID, "simple_id" ), "class" : PageElement(Locators.CLASS_NAME, "simple_class") }
            elements_map = PageElementMap(Locators.CSS_SELECTOR, "#root>div" , key = lambda el : el.text)
            elements_list = PageElements(Locators.CSS_SELECTOR, "#root>div")


        self.driver.execute_script("document.write('%s')" % TrackedElementTest.page_content.replace('\n',''))
        page = SimplePage(self.driver)
        page.elements["id"].click()
        page.elements_map["simple_id"].click()
        page.elements_list[0].click()
        self.assertEquals( [('SimplePage.elements[id]', 'click'), ('SimplePage.elements_map[simple_id]', 'click'), ('SimplePage.elements_list[0]', 'click')],
                self.callback_messages )

