# doctolib

This script checks every n minutues if a new appointment slot for a doctor opened up before a set date. If an appointment is found an sms or email is send to notify the user.


## Setup
- install requirements with poetry https://python-poetry.org/
- if you want to send via a gmail account, you need an app password and cannot use your personal password. get one in your account settings-> security-> bei google anmelden-> app passwords. Alternatively, use another smtp server and change the server name in the script
- if you want to receive the notification per sms, look up the sms gateway for your phone provider. if you found it, send yourself an test email to 0049yourphonenumber@SMSGATEWAYADRESS.de. Your provider might send you an sms request to opt into getting "sms emails". You can confirm that the test email arrived
- if you want to receive the notification per email, use an emailaddress instead
- get API URL for your doctor: Go to the doctolib page, fill out the reason for your visit and copy the url that is requested after you fill in these details, e.g. using chrome developer tools' network tab. Should look similar to https://www.doctolib.de/availabilities.json?start_date=2022-07-03&visit_motive_ids=111111&agenda_ids=11111&insurance_sector=public&practice_ids=111111&limit=14. 


## Script 

Usage :
```
usage: doctolib.py [-h] -a API_URL [-b BOOKING_URL] [-s START_DATE] -e END_DATE -t MAIL_TO -f MAIL_FROM

optional arguments:
  -h, --help            show this help message and exit
  -a API_URL, --api-url API_URL
                        API URL to query for appointments. Should look similar to https://www.doctolib.de/availabilities.json?start_date=2022-07-03&visit_motive_ids=111111
                        &agenda_ids=11111&insurance_sector=public&practice_ids=111111&limit=14. Go to the doctolib page, fill out the reason for your visit and copy the
                        requested url, e.g. using chrome developer tool's network tab.
  -b BOOKING_URL, --booking-url BOOKING_URL
                        Doctolib URL where the user can book the appointment. If present, it will be put into the notification for speedy booking
  -s START_DATE, --start-date START_DATE
                        Start date to look for appointments, format like 2022-07-03
  -e END_DATE, --end-date END_DATE
                        End date to look for appointments, format like 2022-07-03
  -t MAIL_TO, --mail-to MAIL_TO
                        Email receipient of notification, if you send an sms, the format is 0049176...@smsgatewayofphoneprovider.de
  -f MAIL_FROM, --mail-from MAIL_FROM
                        Email sender of notification
```
