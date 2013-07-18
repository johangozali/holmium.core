import multiprocessing.pool
import json
import sys
import optparse
import os
import glob
import shutil
import ConfigParser
import time
import re
import holmium
import subprocess
from xml.dom import minidom
import pkg_resources

acceptable_options = set(["screensize", "remote", "browser","enabled", "useragent"])
screen_size_expr = re.compile("[\(]*(\d+)[x,](\d+)[\)]*")


def prepare_environment( output_dir ):
    """
    simply setup the report directory and back it up if it already exists.
    """
    if os.path.isdir(output_dir):
        shutil.move(output_dir, output_dir + ".%s" % time.strftime("%s", time.localtime()))
    os.mkdir(output_dir)

def sanitize_config(browser_config):
    for browser in browser_config.keys():
        _keys =  set(browser_config[browser].keys())
        if not _keys.issubset( acceptable_options ) and not all([k.startswith("capabilities.") for k in _keys.difference(acceptable_options)]):
            raise AttributeError("%s in section %s are not valid options"
                    % ((",".join(_keys.difference( acceptable_options )), browser)))
        if 'screensize' in _keys:
            try:
                w,h = screen_size_expr.findall(browser_config[browser]['screensize'])[0]
                browser_config[browser]["screensize_width"] = w
                browser_config[browser]["screensize_height"] = h

            except Exception,e:
                raise AttributeError("screensize (%s) for browser %s is invalid. acceptable formats are [n x m or n ,m or (n,m)]"
                        % ( browser_config[browser]["screensize"], browser ))
        if 'enabled' in _keys and int(browser_config[browser]["enabled"]) == 0 :
            browser_config.pop(browser)
            continue

        desired_caps = {}
        for key in [k for k in _keys if k.startswith('capabilities.')]:
            desired_caps[key.replace("capabilities.","")] = browser_config[browser][key]
            browser_config[browser].pop(key)
        browser_config [browser]["desired_capabilities"] = desired_caps

def parse_config( config_file ):
    cfg = ConfigParser.RawConfigParser()
    browser_configs = {}
    global_config = {}
    if not os.path.isfile(config_file):
        raise IOError("config file %s not found" % config_file)
    cfg.read(config_file)
    if cfg.has_section("global"):
        global_config = dict(cfg.items("global"))
    for browser_name in cfg.sections():
        if browser_name == "global":
            continue
        local_config = dict(global_config)
        local_config.update(dict(cfg.items(browser_name)))
        browser_configs[browser_name] = local_config

    sanitize_config(browser_configs)
    return browser_configs

def build_report( output_dir, results_map ):
    if pkg_resources.isdir("holmium.core/res"):
        for res in pkg_resources.resource_listdir("holmium.core","res"):
            data = pkg_resources.resource_stream("holmium.core", "res/"+res).read()
            open(os.path.join(output_dir, res), "w").write(data)
    js_data ={"suites":[]}
    for s in results_map:
        output = results_map[s]
        suite_results = []
        for o in output:
            c = {"name":o}
            c["results"] = output[o].values()
            suite_results.append(c)
        js_data["suites"].append({"suite_name":s, "tests":suite_results})
        open(os.path.join(output_dir, "results.js"), "w").write("var data=%s;" % json.dumps( js_data ) )

def main():
    parser = optparse.OptionParser()
    parser.add_option("","--output-directory",dest = "output", help="output directory for test report", default="holmium_report")
    parser.add_option("","--config-file", dest = "config_file", help="config file to use for tests", default="holmium.cfg")
    parser.add_option("","--num-threads", dest = "num_threads", default=1, help="number of threads used to distribute the execution", type="int")
    parser.add_option("","--with-screenshots", dest = "screenshots", action="store_true", help="include screenshots for each test case")
    parser.add_option("","--nose-args", dest = "noseargs", help="extra arguments to pass to nosetests", default="")

    opts, args = parser.parse_args()
    try:
        prepare_environment( opts.output )
        browser_configs = parse_config ( opts.config_file )
        execution_args = {}
        for friendly_name, config in browser_configs.items():
            noseargs = ["nosetests", "--with-holmium"
            , "--with-xunit"
            , "--xunit-file=%s" % os.path.join(opts.output, friendly_name + ".xunit")
            ]

            if config.has_key("screensize_width") and config.has_key("screensize_height"):
                noseargs +=  ["--holmium-screensize=%s,%s" % ( config["screensize_width"], config["screensize_height"])]
            if config.has_key("remote"):
                noseargs += ["--holmium-remote=%s" % config["remote"]]
            if config.has_key("desired_capabilities"):
                noseargs += ["--holmium-capabilities=%s" % json.dumps(config["desired_capabilities"])]
            if not config.has_key("browser"):
                raise AttributeError("browser option not specified for config section %s" % friendly_name)
            if opts.screenshots:
                noseargs += ["--holmium-screenshot=%s" % (os.path.join(opts.output,friendly_name))]
            if config.has_key("useragent"):
                noseargs += ["--holmium-useragent='%s'" % config["useragent"]]

            noseargs += ["--holmium-browser=%s" % config["browser"]]
            noseargs.extend( [k for k in opts.noseargs.split(" ") if k] )
            noseargs.extend( [k for k in args if k] )
            execution_args[friendly_name] = noseargs

        pool = multiprocessing.pool.ThreadPool(processes=opts.num_threads)
        def worker( arguments ):
            holmium.core.log.info(" ".join(arguments))
            proc = subprocess.Popen( arguments
                                    , stdout = subprocess.PIPE
                                    , stderr = subprocess.PIPE
                                    )
            stdout, stderr = proc.stdout, proc.stderr
            so,se= stdout.read(), stderr.read()

        resp = pool.map_async(worker, execution_args.values())
        while not resp.ready():
            try:
                time.sleep(1)
            except KeyboardInterrupt, e:
                pool.terminate()
                parser.error("stopping on demand")
        resp.get()
        result_map = {}
        for browser in execution_args:
            xunit_file = os.path.join(opts.output, browser + ".xunit")
            try:
                xunit = minidom.parse(xunit_file)
                for suite in xunit.getElementsByTagName("testsuite"):
                    for case in suite.getElementsByTagName("testcase"):
                        classname = case.getAttribute("classname")
                        testname = case.getAttribute("name")
                        error = ""
                        try:
                            error = case.getElementsByTagName("error")[0].getAttribute("message")
                        except Exception:
                            try:
                                error = case.getElementsByTagName("failure")[0].getAttribute("message")
                            except Exception:
                                error = ""
                        if error:
                            status = 0
                        else:
                            status = 1
                        screenshots = []
                        screenshot_json_file = os.path.join(opts.output, browser, classname + "." + testname, "screenshots.json")
                        if os.path.isfile(screenshot_json_file):
                            screenshots = json.load(open(screenshot_json_file))
                        for el in screenshots:
                            el["file"]=el["file"].replace(opts.output,".")
                            screenshots[screenshots.index(el)] = el

                        result_map.setdefault( classname , {})
                        result_map[classname].setdefault( testname , {})
                        result_map[classname][testname][browser]={
                                "name" : testname
                                , "browser": browser
                                , "status": status
                                , "error" : error
                                , "screenshots" : screenshots}

            except Exception,e :
                parser.error("unable to parse xunit output for file %s with error:%s" % (xunit_file,e))
        build_report(opts.output, result_map)
    except Exception,e :
        parser.error(e)


if __name__ == "__main__":
    main()

