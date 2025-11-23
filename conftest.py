import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.safari.options import Options as SafariOptions 
from typing import Literal
import os
import copy

COMMON_BS_OPTIONS = {
    "buildName":"regress",
    "projectName": "regression_suite",
    "networkLogs": "true",
    "consoleLogs": "info",
}

# PLATFORM SPECIFIC: Only contains unique browser/OS/device settings
PLATFORM_SPECIFIC_CAPS = [
    # 1. Desktop Windows 10 Chrome (Original)
    {
        "browserName": "Chrome",
        "browserVersion": "120.0",
        "os": "Windows",
        "osVersion": "10",
        "testName": "Windows 10 Chrome 120.0 Session",
    },

    # 2. Mobile Android Chrome (NEW)
    {
        "browserName": "chrome",
        "osVersion": "11.0",
        "deviceName": "Xiaomi Redmi Note 11",
        "testName": "Xiaomi Redmi Note 11 Session",
    },
    # 3. Desktop OS X Edge (NEW)
    {
        "browserName": "Edge",
        "os": "OS X",
        "osVersion": "Big Sur",
        "testName": "OS X Big Sur Edge Session",
    },
    # 4. Windows 11 Chrome Session (NEW)
    {
        "browserName": "Chrome",
        "browserVersion": "140.0",
        "os": "Windows",
        "osVersion": "11",
        "testName": "Windows 11 Chrome Session",
    },
    # 5. Samsung Galxy S21 session (NEW)
    {
        "browserName": "chrome",
        "osVersion": "11.0",
        "deviceName": "Samsung Galaxy S21",
        "testName": "Samsung Galxy S21 session", 
    },
]

STATIC_BS_CAPABILITIES = []
for caps in PLATFORM_SPECIFIC_CAPS:
    bstack_options = copy.deepcopy(COMMON_BS_OPTIONS)
    final_cap = {}
    
    session_name = caps.pop("testName")
    
    for key, value in caps.items():
        if key in ["browserName", "browserVersion"]:
            final_cap[key] = value
        else:
            bstack_options[key] = value

    bstack_options["sessionName"] = session_name
    final_cap["bstack:options"] = bstack_options
    
    STATIC_BS_CAPABILITIES.append(final_cap)


def pytest_addoption(parser):
    """Adds command-line option for execution mode."""
    parser.addoption("--mode", action="store", default="local", choices=("local", "browserstack"))

@pytest.fixture(scope="session")
def mode(request) -> Literal["local", "browserstack"]:
    """Fixture to retrieve the execution mode selected via command line."""
    return request.config.getoption("--mode")

@pytest.fixture(params=STATIC_BS_CAPABILITIES, scope="function")
def legacy_caps(request, mode):
    """Yields one platform configuration dictionary per test run in BrowserStack mode."""
    if mode == "browserstack":
        return request.param
    return None

def get_browser_options(browser_name: str, maximize: bool):
    """Returns the correct Options object for the given browser."""
    if browser_name == "Safari":
        options = SafariOptions()
    
    elif browser_name in ["Chrome", "chromium"]:
        options = ChromeOptions()
    else:
        
        options = ChromeOptions()

    if maximize:
        
        options.add_argument("--start-maximized")
        
    return options


@pytest.fixture(scope="function")
def driver(mode: Literal["local", "browserstack"], legacy_caps):
    """Initializes and tears down the WebDriver based on the execution mode."""
    
    driver = None
    driver_name = None
    
    if mode == "local":
        print("\nSetting up Local Chrome Driver (Maximized, Performance & Geolocation Optimized)...")
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        
        
        prefs = {
            "profile.default_content_setting_values.geolocation": 2, 
            "profile.managed_default_content_settings.stylesheets": 2, 
            "profile.managed_default_content_settings.fonts": 2,        
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        
        driver = webdriver.Remote(
            command_executor="http://127.0.0.1:4444", 
            options=chrome_options
        )
        driver_name = "local"


    elif mode == "browserstack":
        print("\nSetting up BrowserStack Driver (Manual Multi-Platform Execution)...")
        

        desired_caps = legacy_caps
        
        BROWSERSTACK_USERNAME = "sanskrutiagrawal_WF9Rkw"
        BROWSERSTACK_ACCESS_KEY = ""
        
        if not BROWSERSTACK_USERNAME or not BROWSERSTACK_ACCESS_KEY:
            raise EnvironmentError(
                "BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY environment variables must be set."
            )

        browserstack_url = (
            f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub.browserstack.com/wd/hub"
        )
        
        browser_name = desired_caps.get("browserName", "Chrome")
        

        bs_options = get_browser_options(browser_name, maximize=True)
        
        for key, value in desired_caps.items():
            bs_options.set_capability(key, value)
        
        driver = webdriver.Remote(
            command_executor=browserstack_url,
            options=bs_options
        )
        driver_name = desired_caps.get("bstack:options", {}).get("sessionName", "Unknown")
    
    else:
        raise ValueError(f"Unknown mode: {mode}")

    yield driver, driver_name, legacy_caps


    print("\nQuitting WebDriver...")
    if driver:
        if mode == "browserstack":
            try:
                driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status": "passed"}}')
            except:
                pass
                
        driver.quit()

# import pytest
# import os
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from typing import Literal

# from selenium.webdriver.chrome.options import Options as ChromeOptions 

# def pytest_addoption(parser):
#     """Adds a command-line option to select the execution mode."""
#     parser.addoption(
#         "--mode", action="store", default="local", choices=("local", "browserstack"),
#         help="Execution mode: 'local' (default) or 'browserstack'."
#     )

# @pytest.fixture(scope="session")
# def mode(request) -> Literal["local", "browserstack"]:
#     """Fixture to retrieve the execution mode selected via command line."""
#     return request.config.getoption("--mode")

# @pytest.fixture(scope="function")
# def driver(mode: Literal["local", "browserstack"]):
#     """Initializes and tears down the WebDriver based on the execution mode."""
    
#     driver = None
    
#     if mode == "local":
#         print("\nSetting up Local Chrome Driver (Maximized, Performance & Geolocation Optimized)...")
#         chrome_options = Options()
#         chrome_options.add_argument("--start-maximized")

#         prefs = {
#             "profile.default_content_setting_values.geolocation": 2, 
#             "profile.managed_default_content_settings.stylesheets": 2, 
#             "profile.managed_default_content_settings.fonts": 2,        
#         }
#         chrome_options.add_experimental_option("prefs", prefs)
        
#         driver = webdriver.Chrome(options=chrome_options)
#         driver_name = "local"

#     elif mode == "browserstack":
#         print("\nSetting up BrowserStack Driver (Explicit Remote URL)...")

#         BROWSERSTACK_USERNAME = os.environ.get("BROWSERSTACK_USERNAME")
#         BROWSERSTACK_ACCESS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY")
        
#         if not BROWSERSTACK_USERNAME or not BROWSERSTACK_ACCESS_KEY:
#             raise EnvironmentError(
#                 "BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY environment variables must be set "
#                 "to connect to the BrowserStack hub."
#             )

#         browserstack_url = (
#             f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub.browserstack.com/wd/hub"
#         )

#         bs_options = ChromeOptions()
#         bs_options.add_argument("--start-maximized")
        
#         driver = webdriver.Remote(
#             command_executor=browserstack_url,
#             options=bs_options
#         )
#         driver_name = "bs_remote"
    
#     else:
#         raise ValueError(f"Unknown mode: {mode}")

#     yield driver, driver_name

#     print("\nQuitting WebDriver...")
#     if driver:
#         driver.quit()