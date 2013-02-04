import os
import time
import shutil
import unittest
import inspect
import imp
import holmium
import json
import threading
import multiprocessing.pool
from selenium import webdriver

browser_mapping = {"firefox": webdriver.Firefox,
                    "chrome": webdriver.Chrome,
                    "ie": webdriver.Ie,
                    "opera" : webdriver.Opera,
                    "remote": webdriver.Remote,
                    "phantomjs": webdriver.PhantomJS,
                    "android" : webdriver.Remote}

#:
capabilities = {"firefox": webdriver.DesiredCapabilities.FIREFOX,
                "chrome": webdriver.DesiredCapabilities.CHROME,
                "ie": webdriver.DesiredCapabilities.INTERNETEXPLORER,
                "opera": webdriver.DesiredCapabilities.OPERA,
                "phantomjs":webdriver.DesiredCapabilities.PHANTOMJS,
                "android" : webdriver.DesiredCapabilities.ANDROID}

class Screenshot():
    def __init__(self):
        self.lock = threading.Lock()
        self.inc = 0
        self.last_content = ""
        self.output_dir = None
        self.driver = None
        self.screenshot_mappings = []
        self.threadpool = multiprocessing.pool.ThreadPool(5)
    def _trigger(self, element, action, delay=0):
        try:
            holmium.core.log.debug("triggered screenshot. delaying %ds" % delay)
            time.sleep(delay)
            if self.lock.acquire() and self.driver and self.output_dir:
                screenshot_file = os.path.join(self.output_dir, str(self.inc) + ".png")
                if element and action:
                    label = "%s on %s" % (action , element)
                else:
                    label = ""
                self.screenshot_mappings.append({"file":screenshot_file, "caption":label})
                open(os.path.join(self.output_dir, "screenshots.json"), "w").write(json.dumps(self.screenshot_mappings))
                self.driver.get_screenshot_as_file(screenshot_file)
                self.inc += 1
        except Exception,e:
            holmium.core.log.error("failed to capture screenshot with error %s" % str(e))
        finally:
            self.lock.release()

    def trigger(self, element=None, action  = None):
        self.threadpool.apply( self._trigger, (element, action, 0))

    def set_target(self, driver, name):
        self.driver = driver
        self.output_dir = name
        output_bak = name + "." + time.strftime("%s", time.localtime())
        if os.path.isdir( name ):
            shutil.move(name, output_bak)
        os.makedirs(name)
        self.inc = 0
        self.screenshot_mappings = []



class HolmiumTestCase(unittest.TestCase):
    """
    """

    #:
    @classmethod
    def setUp(self):
        """
        """
        pass

    @classmethod
    def setUpClass(self):
        """
        """
        self.driver = None
        self.screenshots = None
        base_file = inspect.getfile(self)
        config_path = os.path.join(os.path.split(base_file)[0], "config.py")
        try:
            config = imp.load_source("config", config_path)
            self.config = config.config[os.environ.get("HO_ENV", "prod")]
        except IOError:
            holmium.core.log.debug("config.py not found for TestClass %s at %s" %
                                           (self, config_path))

        args = {}
        cap = {}
        driver = os.environ.get("HO_BROWSER", "firefox").lower()
        remote_url = os.environ.get("HO_REMOTE", "").lower()
        if os.environ.get("HO_USERAGENT", ""):
            if driver not in ["chrome","firefox"]:
                raise SystemExit("useragent string can only be overridden for chrome & firefox")
            else:
                if driver == "chrome":
                    cap.update({"chrome.switches":["--user-agent=%s" % os.environ.get("HO_USERAGENT")]})
                elif driver  == "firefox":
                    ffopts = webdriver.FirefoxProfile()
                    ffopts.set_preference("general.useragent.override", os.environ.get("HO_USERAGENT"))
                    if remote_url:
                        args.update({"browser_profile":ffopts})
                    else:
                        args.update({"firefox_profile":ffopts})
        if remote_url:
            cap.update(capabilities[driver])
            args = {"command_executor": remote_url,
                     "desired_capabilities": cap}
            driver = "remote"
        self.driver = browser_mapping[driver](**args)

        if os.environ.get("HO_SCREENSHOT"):
            holmium.core.screenshot_wrapper.set_target(self.driver, os.environ.get("HO_SCREENSHOT"))

    @classmethod
    def tearDownClass(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception,e:
                holmium.core.log.info("failed to terminate driver")

    @classmethod
    def tearDown(self):
        """
        """
        if self.driver:
            self.driver.delete_all_cookies()
