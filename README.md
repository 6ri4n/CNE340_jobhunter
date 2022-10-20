# CNE340_jobhunter
This is an automation script that scrapes data from an API that sends job listings in JSON format.

this script will perform the following every hour:
- makes a request to the API to check the job listings
- inserts any new job listings to a database
- deletes any job listings from the database that are over 14 days old or if they've been taken down
