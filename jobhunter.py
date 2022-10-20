import mysql.connector
import time
import json
import requests
from datetime import date
import html2text


# Connect to database
# You may need to edit the connect function based on your local settings.
# I made a password for my database because it is important to do so. Also make sure MySQL server is running or it will not connect
def connect_to_sql():
    conn = mysql.connector.connect(
        user='root', password='',
        host='127.0.0.1', database='cne340'
    )
    return conn

# Create the table structure
def create_tables(cursor):
    # Creates table
    # Must set Title to CHARSET utf8 unicode Source: http://mysql.rjweb.org/doc.php/charcoll.
    # Python is in latin-1 and error (Incorrect string value: '\xE2\x80\xAFAbi...') will occur if Description is not in unicode format due to the json data
    cursor.execute("CREATE TABLE IF NOT EXISTS jobs (id INT PRIMARY KEY auto_increment, Job_id varchar(50), company varchar (300), Created_at DATE, url varchar(30000), Title LONGBLOB, Description LONGBLOB );")

# Query the database.
# You should not need to edit anything in this function
def query_sql(cursor, query):
    cursor.execute(query)
    return cursor

# Add a new job
def add_new_job(cursor, jobdetails):
    # extract all required columns
    job_id = jobdetails['id']
    date = jobdetails['publication_date'][0:10]
    description = html2text.html2text(jobdetails['description'])
    # %s is what is needed for Mysqlconnector as SQLite3 uses ? the Mysqlconnector uses %s
    query = cursor.execute(
        "INSERT INTO jobs (Job_id, Created_at, Description)"
        "VALUES (%s, %s, %s)", (job_id, date, description)
    )
    return query_sql(cursor, query)

# Check if new job
def check_if_job_exists(cursor, jobdetails):
    ## Add your code here
    job_id = jobdetails['id']
    # queries to see if the job exist in the database
    query = f"SELECT Job_id FROM jobs WHERE Job_id = {job_id}"
    cursor = query_sql(cursor, query)
    # fetchone returns a row -> the job already exist in the database
    # fetchone returns None if no rows are retrieved -> the job would be considered new
    return False if cursor.fetchone() is None else True

# Deletes job
def delete_job(cursor, job_id):
    ## Add your code here
    query = f"DELETE FROM jobs WHERE Job_id = {job_id}"
    return query_sql(cursor, query)

# Grab new jobs from a website, Parses JSON code and inserts the data into a list of dictionaries do not need to edit
def fetch_new_jobs():
    query = requests.get("https://remotive.io/api/remote-jobs")
    datas = json.loads(query.text)
    return datas

# Main area of the code. Should not need to edit
def jobhunt(cursor):
    # Fetch jobs from website
    jobpage = fetch_new_jobs()  # Gets API website and holds the json data in it as a list
    # use below print statement to view list in json format
    #print(jobpage)
    add_or_delete_job(jobpage, cursor)

def add_or_delete_job(jobpage, cursor):
    job_id_from_json = []

    # Add your code here to parse the job page
    for jobdetails in jobpage['jobs']:  # EXTRACTS EACH JOB FROM THE JOB LIST. It errored out until I specified jobs. This is because it needs to look at the jobs dictionary from the API. https://careerkarma.com/blog/python-typeerror-int-object-is-not-iterable/
        # Add in your code here to check if the job already exists in the DB
        # add the job if it doesn't exist in the database - new job listing posted
        if not check_if_job_exists(cursor, jobdetails):
            add_new_job(cursor, jobdetails)
            print(f'++ new job listing posted: {jobdetails}')

        job_id_from_json.append(jobdetails['id'])

    # delete the job from the database if the job listing is removed
    # job listing is removed when the json no longer contains the job id from the database
    query = "SELECT Job_id, Created_at FROM jobs"
    cursor = query_sql(cursor, query)
    job_id_from_db = cursor.fetchall()

    # simulates the removal of a job listing from the API - the job in the database should be removed since the job listing is no longer available
    #latest_job = job_id_from_json.pop()
    #print(f'latest job: {latest_job}')
    #print('start delete section')
    for job_id, job_date in job_id_from_db:
        # EXTRA CREDIT: job listing expires after 14 days
        # https://www.geeksforgeeks.org/python-program-to-find-number-of-days-between-two-given-dates/
        present_date = date.today()
        num_of_days = (present_date - job_date).days

        if int(job_id) not in job_id_from_json or num_of_days > 14:
            delete_job(cursor, int(job_id[0]))
            print(f'-- old job listing removed: {job_id}')
    #print('finished delete section')


# Setup portion of the program. Take arguments and set up the script
# You should not need to edit anything here.
def main():
    # Important, rest are supporting functions
    # Connect to SQL and get cursor
    conn = connect_to_sql()
    cursor = conn.cursor()
    create_tables(cursor)

    while(1):  # Infinite Loops. Only way to kill it is to crash or manually crash it. We did this as a background process/passive scraper
        jobhunt(cursor)
        time.sleep(21600)  # Sleep for 1h, this is ran every hour because API or web interfaces have request limits. Your reqest will get blocked.


# Sleep does a rough cycle count, system is not entirely accurate
# If you want to test if script works change time.sleep() to 10 seconds and delete your table in MySQL
if __name__ == '__main__':
    main()
