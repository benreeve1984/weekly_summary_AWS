import json
import os
from datetime import datetime, timedelta
from garminconnect import Garmin
import garth.http
import math

# Set the user agent to mimic Garmin Connect mobile app
garth.http.USER_AGENT = {'User-Agent': 'GCM-iOS-5.7.2.1'}
print("Initial USER_AGENT:", garth.http.USER_AGENT)

def get_last_week_date_range(reference_date=None):
    """
    Returns the start and end datetime objects for the last week (Monday to Sunday).
    If reference_date is not provided, uses today's date.
    """
    if reference_date is None:
        reference_date = datetime.now()
    # Find the last Monday
    last_monday = reference_date - timedelta(days=reference_date.weekday() + 7)
    last_monday = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    last_sunday = last_monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return last_monday, last_sunday

def fetch_activities(garmin, start_date, end_date):
    """
    Fetches activities from Garmin Connect within the specified date range.
    """
    print(start_date, end_date)
    activities = []
    start = 0
    limit = 100  # Adjust as needed
    while True:
        print("Headers before API call:", garmin.session.headers if hasattr(garmin, 'session') else "No session")
        batch = garmin.get_activities(start, limit)
        if not batch:
            break
        for activity in batch:
            activity_start_time = datetime.strptime(activity['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
            if start_date <= activity_start_time <= end_date:
                activities.append(activity)
        if len(batch) < limit:
            break
        start += limit
    print(activities)
    return activities

# [Include all other helper functions here, as per your original script]

def process_request(event, context):
    """
    AWS Lambda handler function.
    Expects a JSON payload with 'email' and 'password'.
    Returns markdown summary of the last week's activities.
    """
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email and password are required.'})
            }

        # Initialize Garmin client with provided credentials
        garmin = Garmin(email, password)
        garmin.login()
        print("Client headers after login:", garmin.session.headers if hasattr(garmin, 'session') else "No session")

        # Get last week's date range
        today = datetime.now()
        last_week_end = today - timedelta(days=today.weekday() + 1)  # Last Sunday
        last_week_start = last_week_end - timedelta(days=6)  # Last Monday
        start_date, end_date = last_week_start, last_week_end

        # Fetch activities
        activities = fetch_activities(garmin, start_date, end_date)

        # Process activities
        daily_summary, weekly_totals = process_activities(activities)

        # Generate markdown
        markdown = generate_markdown(weekly_totals, daily_summary, last_week_start)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Enable CORS for your static site
            },
            'body': json.dumps({'markdown': markdown})
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# Ensure that the main functions are not executed during Lambda invocation
# Remove or comment out the main block
# if __name__ == "__main__":
#     main()