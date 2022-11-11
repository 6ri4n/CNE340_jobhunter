# Job Hunter
Automation script in Python that retrieves and stores job listings into a MySQL database from an API every hour.

this script will perform the following every hour:
- requests an API for job listings
- storing any new job listings to a database
- removing any job listings from the database if they're over 14 days old or if they're no longer available
