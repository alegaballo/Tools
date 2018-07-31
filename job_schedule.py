'''
This script helps you manage your work schedule, giving you details about how much work you've done and how much you
have left (in terms of hours). 
To use the script run:
python job_schedule.py -s <start_time> [-b <break_time>] [-d <work_day_duation]

Parameters format:
<start_time> HH:MM
<break_time> minutes
<work_day_duration> hours

'''
import argparse
import re
import datetime

def check_start_time(value):
    time=re.match("(\d+):(\d+)", value)
    if not time:
        raise argparse.ArgumentTypeError("%s is an invalid value, start time must be in the format HH:MM" % value)
    match = time.groups()
    hours = int(match[0])
    minutes = int(match[1])
    
    s_time = datetime.time(hours, minutes)
    return s_time
    

def check_break_duration(value):
    duration = float(value)
    if duration < 0 or duration > 120:
        raise argparse.ArgumentTypeError("%s is an invalid value, break time be between 0 and 120 minutes" % value)
    return duration


def check_wday_duration(value):
    duration = int(value)
    
    if duration <= 4 or duration >12:
        raise argparse.ArgumentTypeError("%s is an invalid value, work day duration must be between 4 and 12 hours" 
                                        % value)
    return duration


def get_working_time(args):
    # getting current time
    curr_time = datetime.datetime.time(datetime.datetime.now())
    # converting current time in timedelta
    curr_time = datetime.timedelta(hours=curr_time.hour, minutes=curr_time.minute)
    # converting start time in timedelta
    st_time = datetime.timedelta(hours=args.s.hour, minutes=args.s.minute)
    # converting work duration in timedelta
    work_hours = datetime.timedelta(hours=args.d)
    # converting break time in timedelta
    break_time = datetime.timedelta(minutes=args.b)
    
    # computing the worked time
    work_time = curr_time - st_time - break_time
    # computing the work left
    work_left = work_hours - work_time
    # computing the end time
    end_time = work_left + curr_time
    if work_left.total_seconds() < 0:
        buffer_ = curr_time  - end_time
        print("It's %s, you worked for %s, you have worked %s more, you could have gone home at %s" 
                % (curr_time, work_time, buffer_, end_time))
    else:
        print("It's %s, you worked for %s, you have %s left, you can go home at %s"
                % (curr_time, work_time, work_left, end_time))


def main():
    parser = argparse.ArgumentParser(description = '''Compute your job daily schedule according to start time, 
                                                    break duration and work-day duration''')
    parser.add_argument('-s', type=check_start_time, required=True, help='start time HH:MM')
    parser.add_argument('-b', type=check_break_duration, default=60, help='lunch break duration in MINUTES')
    parser.add_argument('-d', type=check_wday_duration, default=8.0, help='work-day duration in HOURS')
    args = parser.parse_args()
    get_working_time(args)



if __name__ == "__main__":
    main()
