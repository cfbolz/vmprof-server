import pytest
from selenium import webdriver
import selenium.webdriver as webdriver
import selenium.webdriver.support.ui as ui

@pytest.fixture(scope="session")
def drivers(request):
    drivers = [webdriver.Chrome()]
    for b in drivers:
        request.addfinalizer(b.quit)
    return drivers

def _url(path):
    host = "http://localhost:8000"
    if path[0] == "/":
        return host + path
    return host + "/" + path


def query1(elem, q):
    return elem.find_element_by_css_selector(q)

def query(elem, q):
    return elem.find_elements_by_css_selector(q)

def select_trace_entry(driver, wait, entry_name):
    trace_lines = driver.find_elements_by_css_selector("li.trace-entry")
    for line in trace_lines:
        name = line.find_element_by_css_selector(".trace-name").text
        if name != entry_name:
            continue
        line.click()
        wait.until(lambda d: not query1(d, '#loading_img').is_displayed())
        break
    else:
        pytest.fail("could not select %s in log" % entry_name)

class TestTracesView(object):
    def test_display_schedule(self, drivers):
        for driver in drivers:
            wait = ui.WebDriverWait(driver,10)
            driver.get(_url("#/1111/traces"))
            wait.until(lambda d: not query1(d, '#loading_img').is_displayed())

            for elem in driver.find_elements_by_css_selector('li.trace-entry span.trace-name'):
                if 'schedule' in elem.text:
                    break
            else:
                pytest.fail("could not find 'schedule' function in trace view")

    def test_filter_checkboxes(self, drivers):
        for driver in drivers:
            wait = ui.WebDriverWait(driver,10)
            driver.get(_url("#/1111/traces"))
            wait.until(lambda d: not query1(d, '#loading_img').is_displayed())
            for elem in driver.find_elements_by_css_selector('li.trace-entry span.trace-name'):
                if 'schedule' in elem.text:
                    break
            else:
                pytest.fail("could not find 'schedule' function in trace view")


            count = len(driver.find_elements_by_css_selector('li.trace-entry'))

            bridge_checkbox = driver.find_element_by_id("filter_bridge")
            bridge_checkbox.click() # it is now on

            # there must be more bridges filtered
            assert count < len(driver.find_elements_by_css_selector('li.trace-entry'))

            bridge_checkbox.click() # it is now off
            loop_checkbox = driver.find_element_by_id("filter_loop")
            loop_checkbox.click() # do now show loops!

            assert len(driver.find_elements_by_css_selector('li.trace-entry')) == 0
            loop_checkbox.click() # reset to default

    def test_search_traces(self, drivers):
        for driver in drivers:
            wait = ui.WebDriverWait(driver,10)
            driver.get(_url("#/1111/traces"))
            wait.until(lambda d: not query1(d, '#loading_img').is_displayed())
            search_input = driver.find_element_by_id("filter_text")
            search_input.send_keys("schedule")
            assert len(driver.find_elements_by_css_selector('li.trace-entry')) == 1

    def test_load_trace(self, drivers):
        for driver in drivers:
            wait = ui.WebDriverWait(driver,10)
            driver.get(_url("#/1v1/traces"))
            wait.until(lambda d: not query1(d, '#loading_img').is_displayed())
            trace_lines = driver.find_elements_by_css_selector("li.trace-entry")
            for line in trace_lines:
                line.click()
                wait.until(lambda d: not query1(d, '#loading_img').is_displayed())
                names = set()
                for line in driver.find_elements_by_css_selector(".resops > .trace-line"):
                    names.add(query1(line, ".resop-name").text)
                assert len(names) == 2
                assert 'int_add' in names
                assert 'guard_true' in names

    def test_switch_to_opt(self, drivers):
        for driver in drivers:
            wait = ui.WebDriverWait(driver,10)
            driver.get(_url("#/1v1/traces"))
            wait.until(lambda d: not query1(d, '#loading_img').is_displayed())
            select_trace_entry(driver, wait, "funcname1")
            query1(driver, "#switch_trace_opt").click()
            names = set()
            for line in query(driver, ".resops > .trace-line"):
                names.add(query1(line, ".resop-name").text)
            assert len(names) == 3
            assert 'jump' in names
            assert 'int_add' in names
            assert 'guard_true' in names

    def test_display_asm(self, drivers):
        for driver in drivers:
            wait = ui.WebDriverWait(driver,10)
            driver.get(_url("#/1v1/traces"))
            wait.until(lambda d: not query1(d, '#loading_img').is_displayed())
            select_trace_entry(driver, wait, "func_with_nop_assembly")
            #
            query1(driver, "#switch_trace_asm").click()
            asm = []
            for line in query(driver, ".trace-asm-line > div"):
                asm.append(line.text.strip())
            assert asm == ["nop"] * 3
