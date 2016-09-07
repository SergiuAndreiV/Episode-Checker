#
# Check if new episodes are available from "Mr. Robot" season 2
#
# ==============================================================
# TODO - Multi Threading execution
#      - add a time stamp after sending an email
#    * - read attributes from XML
# ==============================================================

from email.mime.text import MIMEText
import xml.etree.cElementTree as ET
import requests
import smtplib
import time
import bs4


tree = ET.parse("date_serial.xml")
root = tree.getroot()
nrEpisoade = int(tree.findtext("episoade"))
print(nrEpisoade, "episodes available")

# where the mail will be sent
eRecTree = ET.parse("email_recivers.xml")
emailRecRoot = eRecTree.getroot()
email_recivers_list = eRecTree.findall("email")

sender_xmltree = ET.parse("sender_info.xml")


# SENDER INFO
account = sender_xmltree.findtext("email")
sender = sender_xmltree.findtext("email")
password = sender_xmltree.findtext("pass")
servar = sender_xmltree.findtext("servar")
port = int(sender_xmltree.find("servar").attrib['port'])
print(port, type(port))

print("--------------------")
print("servar:", servar, "PORT:", port)
for x in email_recivers_list:
    print(x.text)
print("--------------------")

receivers = [x.text for x in email_recivers_list]

sec = 60  # seconds to sleep
inc = 0


def findNewEpisode():

    global inc

    time.sleep(sec)
    print(inc / 60, "minutes has passed!", end="\r")
    inc += sec

    tree = ET.parse("date_serial.xml")
    root = tree.getroot()

    try:
        res = requests.get("http://www.pelispedia.tv/serie/mr-robot/")
        res.raise_for_status()
        MrRobot_soup = bs4.BeautifulSoup(res.text, "lxml")
        new = len(MrRobot_soup.select(".bpM81 li"))
    except:
        print("Unable to fetch requests!", "\r")

    nrEpisoade = int(tree.findtext("episoade"))

    if new > nrEpisoade:

        # build email info (e.g. Subject, from, to ...)
        try:
            with open("textMail.html") as fp:
                msg = MIMEText(fp.read(), "html")

            msg["Subject"] = """"Mr. Robot" - Episode """ + \
                str(new - 10) + """ is available!"""
            msg["From"] = sender
            msg["To"] = ", ".join(receivers)
            msg_full = msg.as_string()
        except:
            print("Error in trying to build email info")

        # try to send email
        try:
            smtpObj = smtplib.SMTP(servar, port)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.ehlo()
            smtpObj.verify(account)
            smtpObj.login(account, password)
            smtpObj.sendmail(account, receivers, msg_full)
            smtpObj.quit()
            print("Successfully sent email to |", " | ".join(receivers))
        except:
            print("Error: unable to send email")

        # webbrowser.open("http://www.pelispedia.tv/serie/mr-robot/")
        # print("http://www.pelispedia.tv/serie/mr-robot/")

        # update xml file to last episoade
        root.remove(root.find("episoade"))
        ET.SubElement(root, "episoade").text = str(new)
        tree.write("date_serial.xml")

    else:
        print("No new espisodes!        ", end="\r")

if __name__ == "__main__":
    while True:
        findNewEpisode()
