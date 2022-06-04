import argparse
import json
import re
import smtplib
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from getpass import getpass

from loguru import logger

EXAMPLE_URL = "https://www.doctolib.de/availabilities.json?start_date=2022-07-03&visit_motive_ids=111111&agenda_ids=11111&insurance_sector=public&practice_ids=111111&limit=14"


def get_response(url):
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ",
        "Connection": "keep-alive",
    }
    req = urllib.request.Request(url=url, headers=header)
    response_json = urllib.request.urlopen(req).read().decode()
    response = json.loads(response_json)
    return response


def find_slot(start_date, end_date, url):
    assert (
        end_date > start_date
    ), f"end_date {end_date} must be after start_date {start_date}"
    all_slots = []
    timeframe = 14
    # url = "https://www.doctolib.de/availabilities.json?start_date=2022-06-03&visit_motive_ids=2208297&agenda_ids=351747&insurance_sector=private&practice_ids=139285&limit=3"
    url = re.sub("limit=[0-9]*", "limit=%i" % timeframe, url)

    for s in [
        start_date + timedelta(days=i)
        for i in range(0, (end_date - start_date).days, timeframe)
    ]:
        url = re.sub(
            "start_date=..........", "start_date=%s" % s.strftime("%Y-%m-%d"), url
        )
        logger.debug(f"Checking URL {url}")

        availabilities = get_response(url)["availabilities"]
        slots = [
            datetime.fromisoformat(slot).strftime("%d.%m. %H:%M")
            for entry in availabilities
            for slot in entry["slots"]
            if entry["slots"]
        ]
        all_slots.extend(slots)

    logger.info(f"Found the following slots: {all_slots}")
    return all_slots


def notify(slots, booking_url, sender_email, sender_pw, recipient_email):

    message_body = (
        f"New doctor appointment slots on {booking_url}: {slots}, please go immediately"
        " and book them"
    )
    send_mail(sender_email, sender_pw, recipient_email, message=message_body)


def send_mail(sender, sender_password, receipient, message):
    """
    Sends a mail
    """
    client = None
    try:
        client = smtplib.SMTP("smtp.gmail.com", 587)
        client.starttls()
        client.login(sender, sender_password)
        client.sendmail(sender, [receipient], message)
        logger.info("Successfully sent email")
    except Exception as e:
        logger.exception(e)
    finally:
        if client is not None:
            client.quit()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--api-url",
        required=True,
        help=(
            f"API URL to query for appointments. Should look similar to {EXAMPLE_URL}."
            " Go to the doctolib page, fill out the reason for your visit and copy the"
            " requested url, e.g. using chrome developer tool's network tab."
        ),
    )

    parser.add_argument(
        "-b",
        "--booking-url",
        required=False,
        default="https://www.doctolib.de",
        help=(
            "Doctolib URL where the user can book the appointment. If present, it will"
            " be put into the notification for speedy booking"
        ),
    )

    parser.add_argument(
        "-s",
        "--start-date",
        default=datetime.today().replace(hour=0, minute=0, second=0, microsecond=0),
        help="Start date to look for appointments, format like 2022-07-03",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d") if type(s) == "str" else s,
    )

    parser.add_argument(
        "-e",
        "--end-date",
        required=True,
        help="End date to look for appointments, format like 2022-07-03",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    )

    parser.add_argument(
        "-t",
        "--mail-to",
        required=True,
        help=(
            "Email receipient of notification, if you send an sms, the format is"
            " 0049176...@smsgatewayofphoneprovider.de"
        ),
    )

    parser.add_argument(
        "-f",
        "--mail-from",
        required=True,
        help="Email sender of notification",
    )

    arguments = parser.parse_args(argv)
    assert (
        "gmail" in arguments.mail_from
    ), "Sender must be a gmail address. if not, change smtp server"

    pwd = getpass("SMTP password for the sender")

    url = arguments.api_url

    slots = []
    wait_in_sec = 60 * 5
    while True and not slots:
        slots = find_slot(arguments.start_date, arguments.end_date, url)
        if slots:
            notify(
                slots,
                arguments.booking_url,
                arguments.mail_from,
                pwd,
                arguments.mail_to,
            )
        time.sleep(wait_in_sec)


if __name__ == "__main__":
    sys.exit(main())
