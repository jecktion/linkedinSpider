import argparse
import gc
import random
import smtplib
import sys
import time
import unicodedata
from smtplib import SMTPException

import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from stem import Signal
from stem.control import Controller

controller = Controller.from_port(port=9051)


def releaseList(a):
    del a[:]
    del a


def SendMail(pidNumber, pidEnd):
    sender = '*********'
    reciever = ['*********']
    message = """
              From: Anil Pediredla<**************>
              To: Anil Pediredla<************>
              Subject: Failed Job

              l393n812
              Switch@2016

              From process running at host: manx.ittc.ku.edu with Tor service 9050
              terminated with start pid as
              """ + pidNumber + " and ending pid as " + pidEnd
    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(sender, '**********')
        smtpObj.sendmail(sender, reciever, message)
        smtpObj.close()
        sys.exit(0)
    except SMTPException:
        print ("Everything failed")
        sys.exit(1)


def newIdentity():
    controller.authenticate()
    controller.signal(Signal.RELOAD)


def FirefoxProfileSettings():
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.socks', '127.0.0.1')
    profile.set_preference('network.proxy.socks_port', 9050)

    return profile


def normText(unicodeText):
    return unicodedata.normalize('NFKD', unicodeText).encode('ascii', 'ignore')


def ConnectDatabase():
    conn = pymysql.connect(host='*********',
                           user='root',
                           db='linkedin',
                           passwd='*********',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    return conn


def queryTable(newPerson):
    conn = ConnectDatabase()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO `newData`(`pid`,`first`,`last`,`name`,`cw`,`title`,`affiliation`,`location`,`industry`,`school`,`degree`,`timeperiod`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                newPerson)
            # result = cursor.fetchone()

        conn.commit()
    finally:
        conn.close()


def reloadOnCaught(browser, pidNumberStart, pidEnd):
    response = True
    i = 0
    browser.get("https://www.linkedin.com/in/jeffweiner08")
    time.sleep(5)
    while response:
        time.sleep(5)
        try:
            if browser.find_element_by_id('first-name') or browser.find_element_by_id(
                    'session_key-login') or browser.find_element_by_class_name(
                'nav-link') or browser.find_element_by_id('denialUrl'):
                print ("linked in found us, change identity!!")
                newIdentity()
                # browser.quit()
                browser.quit()
                gc.collect()
                i += 1
                time.sleep(2)
                newbrowser = webdriver.Firefox(firefox_profile=FirefoxProfileSettings())
                # time.sleep(random.uniform(10, 20))
                newbrowser.get("https://www.linkedin.com/in/jeffweiner08")
                browser = newbrowser
                del newbrowser

            else:
                response = False

        except NoSuchElementException as noe:
            response = False

        except OSError as ose:
            SendMail(pidNumberStart, pidEnd)
    return browser


def writeTofile(content):
    page = BeautifulSoup(content, 'html.parser')
    wfile = open(page.title.string.replace("/", "") + ".html", "w")
    content = normText(page.prettify())
    wfile.write(content)
    wfile.close()


def appendUrl(url):
    ofile = open("urlRepo.txt", "a")
    ofile.write("\n" + url)
    ofile.close()


def normText(unicodeText):
    return unicodedata.normalize('NFKD', unicodeText).encode('ascii', 'ignore')


def viewBot(browser, pidNumberStart, pidNumberEnd):
    # browser = reloadOnCaught(browser)
    conn = ConnectDatabase()
    browsers = [browser]
    i = 0
    trap = 0
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT DISTINCT * FROM `pea` where (pid >=' + pidNumberStart + ' and pid<=' + pidNumberEnd + ') GROUP BY pid')
            results = cursor.fetchall()

        conn.commit()

    finally:
        conn.close()

    print ("got results")
    count = len(results)

    if results:
        for result in results:  # while i < len(results)
            values = [result['pid'], result['first'], result['last'], result['name']]
            foundLink = None
            school = "noSchool"
            degree = "noDegree"
            timeperiod = "noTime"

            time.sleep(random.uniform(5, 10))

            try:
                if browser.find_element_by_class_name('nav-link') or browser.find_element_by_id(
                        'session_key-login') or browser.find_element_by_id('first-name'):
                    newBrowser = reloadOnCaught(browser, str(result['pid']), pidNumberEnd)
                    # os.kill(browser.binary.process.pid, signal.SIGTERM)
                    browser = newBrowser
                    del newBrowser

            except NoSuchElementException as noe0:
                print ("good to go!")

            try:
                firstNameElement = browser.find_element_by_id("firstName")
                lastNameElement = browser.find_element_by_id("lastName")
                firstNameElement.clear()
                lastNameElement.clear()
                lastNameElement.send_keys(result['last'])
                firstNameElement.send_keys(result['first'])
                lastNameElement.submit()

                count -= 1

                print ("[+] Sucess, bot will start crawling")
                print (str(count) + " remaining")

                if not browser.find_elements_by_class_name('fn'):
                    print ("page has results checking headlines")
                    try:
                        if browser.find_element_by_id('first-name') or browser.find_element_by_class_name(
                                'nav-link') or browser.find_element_by_id(
                                'session_key-login') or browser.find_element_by_id('denialUrl'):
                            newBrowser = reloadOnCaught(browser, str(result['pid']), pidNumberEnd)
                            # os.kill(browser.binary.process.pid, signal.SIGTERM)
                            browser = newBrowser
                            del newBrowser
                            continue
                    except NoSuchElementException as noe1:
                        print ("check the anchors!!")
                    elements = browser.find_elements_by_class_name('headline')
                    if elements:
                        # print "here I am!"
                        for element in elements:
                            # print "here in for loop"
                            div = element.find_elements_by_xpath(
                                "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'" +
                                result['school'] + "')]")
                            div1 = element.find_elements_by_xpath(
                                "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'" +
                                result['cw'] + "')]")
                            div2 = element.find_elements_by_xpath(
                                "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'" +
                                result['affiliation'] + "')]")
                            if div or div1 or div2:
                                print ("checking anchors")
                                anchors = element.find_elements_by_xpath('..')

                                for anchor in anchors:
                                    # print "here in anchors"
                                    if (normText(result['school']).lower() in normText(anchor.text).lower()) or (
                                                normText(result['affiliation']).lower() in normText(
                                                anchor.text).lower()) or (
                                                normText(result['cw']).lower() in normText(anchor.text).lower()):
                                        print ("found original person")
                                        foundLink = anchor.find_element_by_css_selector('a')
                                        # end of finding person
                                        # end of div tags
                                        # end of for elements
                            else:
                                print ("writing everything to file")
                                writeTofile(browser.page_source)
                    # end of if elements
                    try:
                        browser.get(foundLink.get_attribute("href"))
                        if browser.find_element_by_id('first-name') or browser.find_element_by_id(
                                'session_key-login') or browser.find_element_by_class_name(
                            'nav-link') or browser.find_element_by_id('denialUrl'):
                            newBrowser = reloadOnCaught(browser, str(result['pid']), pidNumberEnd)
                            # os.kill(browser.binary.process.pid, signal.SIGTERM)
                            browser = newBrowser
                            del newBrowser
                    except AttributeError as attrErr:
                        print ("writing everything to file")
                        writeTofile(browser.page_source)
                        continue
                    except NoSuchElementException as noe2:
                        print ("good to go!!")

                appendUrl(browser.current_url)
                values.append(browser.find_element_by_xpath('//p[@data-section="headline"]').text)
                values.append(browser.find_element_by_class_name("item-title").text)
                values.append(browser.find_element_by_class_name("item-subtitle").text)
                values.append(browser.find_element_by_class_name("locality").text)
                values.append(browser.find_element_by_class_name("descriptor").text)
                values.append(school)
                values.append(degree)
                values.append(timeperiod)

                if browser.find_elements_by_id("education"):
                    education = browser.find_element_by_id("education")
                    if type(education) is list:
                        for edu in education:
                            values.remove(school)
                            values.remove(degree)
                            values.remove(timeperiod)

                            try:

                                if edu.find_element_by_class_name("item-title") is list:
                                    for sch in edu.find_element_by_class_name("item-title"):
                                        school = sch.text
                                else:
                                    school = edu.find_element_by_class_name("item-title").text
                            except NoSuchElementException:
                                school = ""

                            try:
                                if edu.find_element_by_class_name("item-subtitle") is list:
                                    for deg in edu.find_element_by_class_name("item-subtitle"):
                                        degree = deg.text
                                else:
                                    degree = edu.find_element_by_class_name("item-subtitle").text
                            except NoSuchElementException:
                                degree = ""
                            try:
                                if edu.find_element_by_class_name("date-range") is list:
                                    for ti in edu.find_element_by_class_name("date-range"):
                                        timeperiod = ti.text
                                else:
                                    timeperiod = edu.find_element_by_class_name("date-range").text
                            except NoSuchElementException:
                                timeperiod = ""

                            values.append(school)
                            values.append(degree)
                            values.append(timeperiod)

                            queryTable(tuple(values))

                            print (tuple(values))
                    else:
                        try:
                            if education.find_element_by_class_name("item-title"):
                                values.remove(school)
                                values.remove(degree)
                                values.remove(timeperiod)
                                school = browser.find_element_by_class_name("item-title").text
                                values.append(school)
                                values.append(degree)
                                values.append(timeperiod)
                        except NoSuchElementException:
                            values.remove(school)
                            values.remove(degree)
                            values.remove(timeperiod)
                            school = ""
                            values.append(school)
                            values.append(degree)
                            values.append(timeperiod)

                        try:
                            if education.find_element_by_class_name("item-subtitle"):
                                values.remove(degree)
                                values.remove(timeperiod)
                                degree = education.find_element_by_class_name("item-subtitle").text
                                values.append(degree)
                                values.append(timeperiod)
                        except NoSuchElementException:
                            values.remove(degree)
                            values.remove(timeperiod)
                            degree = ""
                            values.append(degree)
                            values.append(timeperiod)
                        try:
                            if education.find_element_by_class_name("date-range"):
                                values.remove(timeperiod)
                                timeperiod = education.find_element_by_class_name("date-range").text
                                values.append(timeperiod)
                            queryTable(tuple(values))
                        except NoSuchElementException:
                            values.remove(timeperiod)
                            timeperiod = ""
                            values.append(timeperiod)

                        print (tuple(values))
                writeTofile(browser.page_source)
            except NoSuchElementException as Noe:
                print ("stacktrace: %s" % Noe)
                if "firstName" in Noe.msg:
                    print ("it's a trap, reload")
                    trap += 1
                    if trap == 15:
                        SendMail(str(result['pid']), pidNumberEnd)
                    newBrowser = reloadOnCaught(browser, str(result['pid']), pidNumberEnd)
                    # browser.quit()
                    browser = newBrowser
                continue
            except StaleElementReferenceException as sle:
                print ("I am writing all to file")
                writeTofile(browser.page_source)
                # endof for loop
                # end of if results


def main(start, end):
    browser = [webdriver.Firefox(firefox_profile=FirefoxProfileSettings())]
    browser[0].get("https://www.linkedin.com/in/jeffweiner08")
    i = 0
    time.sleep(5)
    try:
        if browser[i].find_element_by_id('first-name') or browser[i].find_element_by_id('session_key-login'):
            browser.append(reloadOnCaught(browser[i], start, end))
            i += 1
    except NoSuchElementException:
        print ("good to go!!")
    newBrowser = browser[i]
    releaseList(browser)
    gc.collect()
    viewBot(newBrowser, str(start), str(end))
    newBrowser.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Enter pid number to start with and pid to end at')
    parser.add_argument('-s', action="store", dest="pid_start", type=int)
    parser.add_argument('-e', action="store", dest="pid_end", type=int)
    result = parser.parse_args()
    try:
        main(result.pid_start, result.pid_end)
    except Exception as mom:
        print ("stacktrace is: %s" % mom)
        SendMail(str(result.pid_start), str(result.pid_end))
    except OSError as e:
        print ("stacktrace is: %s" % e)
        SendMail(str(result.pid_start), str(result.pid_end))
