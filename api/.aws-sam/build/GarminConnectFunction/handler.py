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

def calculate_pace(duration_seconds, distance_meters, per_meter=True):
    """
    Calculates pace.
    If per_meter is True, returns seconds per meter.
    Else, returns seconds per kilometer or per 100m based on distance.
    """
    if distance_meters == 0:
        return 0
    if per_meter:
        pace_seconds = duration_seconds / distance_meters
        return pace_seconds
    else:
        pace_seconds = duration_seconds / (distance_meters / 1000)  # seconds per km
        return pace_seconds

def format_pace(pace_seconds):
    """
    Formats pace from seconds to mm:ss format.
    """
    if pace_seconds == 0:
        return "N/A"
    minutes = int(pace_seconds // 60)
    seconds = int(round(pace_seconds % 60))
    return f"{minutes}:{seconds:02d}/km"

def format_pace_swim(pace_seconds):
    """
    Formats swim pace from seconds to mm:ss/100m format.
    """
    if pace_seconds == 0:
        return "N/A"
    minutes = int(pace_seconds // 60)
    seconds = int(round(pace_seconds % 60))
    return f"{minutes}:{seconds:02d}/100m"

def calculate_ef_run(duration_seconds, distance_meters, avg_hr):
    """
    Calculates TrainingPeaks Efficiency Factor for running.
    """
    yards = distance_meters * 1.09361
    minutes = duration_seconds / 60
    if minutes == 0 or avg_hr == 0:
        return 0
    ef = (yards / minutes) / avg_hr
    return round(ef, 2)

def calculate_ef_bike(avg_power, avg_hr):
    """
    Calculates TrainingPeaks Efficiency Factor for biking.
    """
    if avg_hr == 0:
        return 0
    ef = avg_power / avg_hr
    return round(ef, 2)

def map_activity_type(activity_type):
    """
    Maps detailed activity types to general categories.
    """
    mapping = {
        'cycling': 'cycling',
        'indoor_cycling': 'cycling',
        'running': 'running',
        'lap_swimming': 'lap_swimming',
    }
    return mapping.get(activity_type.lower(), None)

def process_activities(activities):
    """
    Processes activities and organizes them by day.
    Also calculates weekly totals and summary metrics.
    """
    daily_summary = {}
    weekly_totals = {}
    summary_metrics = {
        'running': {
            'count': 0,
            'total_duration': 0,
            'total_distance': 0,
            'total_pace': 0,
            'total_ef': 0,
            'total_hr': 0,
            'count_hr': 0
        },
        'cycling': {
            'count': 0,
            'total_duration': 0,
            'total_distance': 0,
            'total_power': 0,
            'total_ef': 0,
            'total_hr': 0,
            'count_hr': 0
        },
        'lap_swimming': {
            'count': 0,
            'total_duration': 0,
            'total_distance': 0,
            'total_pace': 0,
            'total_hr': 0,
            'count_hr': 0
        }
    }
    
    for activity in activities:
        activity_start = datetime.strptime(activity['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
        date_str = activity_start.strftime('%a %d %b')
        if date_str not in daily_summary:
            daily_summary[date_str] = []
        
        activity_type_raw = activity['activityType']['typeKey']
        activity_type = map_activity_type(activity_type_raw)
        
        if not activity_type:
            continue
        
        duration = timedelta(seconds=int(activity['duration']))
        duration_seconds = duration.total_seconds()
        duration_str = f"{int(duration_seconds // 3600)}h {int((duration_seconds % 3600) // 60)}m" if duration_seconds >= 3600 else f"{int(duration_seconds // 60)} mins"
        
        avg_hr = int(activity.get('averageHR', 0))
        if avg_hr > 0:
            summary_metrics[activity_type]['total_hr'] += avg_hr
            summary_metrics[activity_type]['count_hr'] += 1
        
        # Process specific activity types
        if activity_type == 'running':
            distance_km = activity['distance'] / 1000
            pace_sec_per_km = calculate_pace(activity['duration'], activity['distance'], per_meter=False)
            pace_str = format_pace(pace_sec_per_km)
            ef = calculate_ef_run(activity['duration'], activity['distance'], avg_hr)
            activity_info = f"Run: {duration_str}; HR {avg_hr}; pace {pace_str}; EF {ef}"
            
            summary_metrics['running'].update({
                'count': summary_metrics['running']['count'] + 1,
                'total_duration': summary_metrics['running']['total_duration'] + duration_seconds,
                'total_distance': summary_metrics['running']['total_distance'] + activity['distance'],
                'total_pace': summary_metrics['running']['total_pace'] + pace_sec_per_km,
                'total_ef': summary_metrics['running']['total_ef'] + ef
            })
            
        elif activity_type == 'lap_swimming':
            pace_sec_per_100m = (calculate_pace(activity['duration'], activity['distance'], per_meter=False)) / 10
            pace_str = format_pace_swim(pace_sec_per_100m)
            activity_info = f"Swim: {duration_str}; HR {avg_hr}; pace {pace_str}"
            
            summary_metrics['lap_swimming'].update({
                'count': summary_metrics['lap_swimming']['count'] + 1,
                'total_duration': summary_metrics['lap_swimming']['total_duration'] + duration_seconds,
                'total_distance': summary_metrics['lap_swimming']['total_distance'] + activity['distance'],
                'total_pace': summary_metrics['lap_swimming']['total_pace'] + pace_sec_per_100m
            })
            
        elif activity_type == 'cycling':
            avg_power = int(activity.get('avgPower', 0))
            ef = calculate_ef_bike(avg_power, avg_hr)
            activity_info = f"Bike: {duration_str}; HR {avg_hr}; Power {avg_power}w; EF {ef}"
            
            summary_metrics['cycling'].update({
                'count': summary_metrics['cycling']['count'] + 1,
                'total_duration': summary_metrics['cycling']['total_duration'] + duration_seconds,
                'total_distance': summary_metrics['cycling']['total_distance'] + activity['distance'],
                'total_power': summary_metrics['cycling']['total_power'] + avg_power,
                'total_ef': summary_metrics['cycling']['total_ef'] + ef
            })
        
        daily_summary[date_str].append(activity_info)
    
    # Calculate weekly totals
    for activity_type, metrics in summary_metrics.items():
        if metrics['count'] > 0:
            weekly_totals[activity_type] = {
                'sessions': metrics['count'],
                'total_duration': str(timedelta(seconds=int(metrics['total_duration']))),
                'total_distance_km': round(metrics['total_distance'] / 1000, 2),
                'average_hr': round(metrics['total_hr'] / metrics['count_hr'], 2) if metrics['count_hr'] > 0 else "N/A"
            }
            
            if activity_type == 'running':
                weekly_totals[activity_type].update({
                    'average_pace': format_pace(metrics['total_pace'] / metrics['count']),
                    'average_ef': round(metrics['total_ef'] / metrics['count'], 2)
                })
            elif activity_type == 'cycling':
                weekly_totals[activity_type].update({
                    'average_power': round(metrics['total_power'] / metrics['count'], 2),
                    'average_ef': round(metrics['total_ef'] / metrics['count'], 2)
                })
            elif activity_type == 'lap_swimming':
                weekly_totals[activity_type]['average_pace'] = format_pace_swim(metrics['total_pace'] / metrics['count'])
    
    return daily_summary, weekly_totals

def generate_markdown(weekly_totals, daily_summary, week_start_date):
    """
    Generates markdown formatted weekly summary.
    """
    week_start_str = week_start_date.strftime('%d %b %Y')
    markdown = f"**Weekly Summary - {week_start_str}**\n\n"
    
    if weekly_totals:
        markdown += "### Summary Metrics\n\n"
        for activity_type, totals in weekly_totals.items():
            if activity_type == 'running':
                markdown += f"**Running**\n"
                markdown += f"- Sessions: {totals['sessions']}\n"
                markdown += f"- Total Duration: {totals['total_duration']}\n"
                markdown += f"- Total Distance: {totals['total_distance_km']} km\n"
                markdown += f"- Average Pace: {totals['average_pace']}\n"
                markdown += f"- Average EF: {totals['average_ef']}\n"
                markdown += f"- Average HR: {totals['average_hr']} bpm\n\n"
            elif activity_type == 'cycling':
                markdown += f"**Cycling**\n"
                markdown += f"- Sessions: {totals['sessions']}\n"
                markdown += f"- Total Duration: {totals['total_duration']}\n"
                markdown += f"- Total Distance: {totals['total_distance_km']} km\n"
                markdown += f"- Average Power: {totals['average_power']} W\n"
                markdown += f"- Average EF: {totals['average_ef']}\n"
                markdown += f"- Average HR: {totals['average_hr']} bpm\n\n"
            elif activity_type == 'lap_swimming':
                markdown += f"**Swimming**\n"
                markdown += f"- Sessions: {totals['sessions']}\n"
                markdown += f"- Total Duration: {totals['total_duration']}\n"
                markdown += f"- Total Distance: {totals['total_distance_km']} km\n"
                markdown += f"- Average Pace: {totals['average_pace']}\n"
                markdown += f"- Average HR: {totals['average_hr']} bpm\n\n"
    
    markdown += "### Daily Activities\n\n"
    for i in range(7):
        day = week_start_date + timedelta(days=i)
        date_str = day.strftime('%a %d %b')
        activities = daily_summary.get(date_str, [])
        markdown += f"**{date_str}**\n"
        if activities:
            for activity in activities:
                markdown += f"- {activity}\n"
        else:
            markdown += "- Rest day\n"
        markdown += "\n"
    
    return markdown

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