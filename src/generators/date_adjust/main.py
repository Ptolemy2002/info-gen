from datetime import datetime, timedelta
from typing import cast
from generators.date import len_month, loop_month_int, KnownFloatingHoliday, FLOATING_HOLIDAY_MAP, IntMonthDayPair, which_known_holiday
from utils import do_while
from .pytypes import DateAdjustArgs

def gen_date_adjust(args: DateAdjustArgs, log: bool = False) -> str:
    input_format = args['input_format']
    output_format = args['output_format']

    base_date = args.get('date')
    base_date = datetime.strptime(base_date, input_format) if base_date is not None else None

    if base_date is None:
        raise ValueError("The date argument is required for date adjustment.")
    
    result_date = base_date
    og_date = base_date

    def result_date_str() -> str:
        nonlocal result_date
        return result_date.strftime(output_format)

    def result_date_str_notime() -> str:
        nonlocal result_date
        return result_date.strftime("%Y-%m-%d")

    if log: print(f"Base date: {result_date_str()}")

    duration = args['duration']

    if duration['seconds'] != 0:
        if log: print(f"Adjusting date by {duration['seconds']} seconds")
        result_date += timedelta(seconds=duration['seconds'])
        if log: print(f"New date: {result_date_str()}")

    if duration['minutes'] != 0:
        if log: print(f"Adjusting date by {duration['minutes']} minutes")
        result_date += timedelta(minutes=duration['minutes'])
        if log: print(f"New date: {result_date_str()}")

    if duration['hours'] != 0:
        if log: print(f"Adjusting date by {duration['hours']} hours")
        result_date += timedelta(hours=duration['hours'])
        if log: print(f"New date: {result_date_str()}")

    if duration['days'] != 0:
        if log: print(f"Adjusting date by {duration['days']} days")
        result_date += timedelta(days=duration['days'])
        if log: print(f"New date: {result_date_str_notime()}")

    if duration['weekdays'] != 0:
        # Similar to days, but skip Saturdays and Sundays. Step one day at a time in the appropriate direction.
        if log: print(f"Adjusting date by {duration['weekdays']} weekdays")
        direction = 1 if duration['weekdays'] > 0 else -1
        weekdays_added = 0
        target = abs(duration['weekdays'])
        while weekdays_added < target:
            result_date += timedelta(days=direction)
            if result_date.weekday() < 5:  # Monday=0, Sunday=6
                weekdays_added += 1
        
        if log: print(f"New date: {result_date_str_notime()}")

    if duration['weeks'] != 0:
        if log: print(f"Adjusting date by {duration['weeks']} weeks")
        result_date += timedelta(weeks=duration['weeks'])
        if log: print(f"New date: {result_date_str_notime()}")

    if duration['months'] != 0:
        if log: print(f"Adjusting date by {duration['months']} months")

        month_length = args['month_length']

        if month_length is None:
            new_month, new_year = loop_month_int(result_date.month, result_date.year, duration['months'])

            # If the target month has fewer days than the current day, spill overflow days into
            # the next month (if adding months), or clamp to the last day of the target month
            # (if subtracting months).
            # e.g. Jan 31 + 1 month -> Feb can't hold day 31, excess 3 spills into Mar -> Mar 3
            # e.g. Mar 31 - 1 month -> Feb can't hold day 31, clamp to Feb 28
            days_in_new_month = len_month(new_year, new_month)
            new_day = result_date.day

            if new_day > days_in_new_month:
                excess = new_day - days_in_new_month
                if duration['months'] > 0:
                    if log: print(f"Month {new_month} in year {new_year} has only {days_in_new_month} days, spilling excess {excess} into next month")
                    new_month, new_year = loop_month_int(new_month, new_year, 1)
                    new_day = excess
                else:
                    if log: print(f"Month {new_month} in year {new_year} has only {days_in_new_month} days, clamping to last day")
                    new_day = days_in_new_month

            result_date = result_date.replace(year=new_year, month=new_month, day=new_day)
        else:
            if log: print(f"Using static month_length of {month_length} days")
            # If month_length is provided, treat each month as having that many days. Just add the appropriate number of days.
            result_date += timedelta(days=duration['months'] * month_length)
        
        if log: print(f"New date: {result_date_str_notime()}")

    if duration['years'] != 0:
        if log: print(f"Adjusting date by {duration['years']} years")
        new_year = result_date.year + duration['years']
        try:
            result_date = result_date.replace(year=new_year)
        except ValueError:
            # Feb 29 in a non-leap target year -> use March 1
            if log: print(f"Year {new_year} is not a leap year, adjusting Feb 29 to Mar 1")
            result_date = result_date.replace(year=new_year, month=3, day=1)
        if log: print(f"New date: {result_date_str_notime()}")

    # Adjust result_date forward until it is not a holiday or (if skip_weekends is True) a weekend.
    holidays = args['holidays']
    # Split the holiday list into fixed and floating, since they need to be handled differently.
    fixed_holidays = [h for h in holidays if isinstance(h, tuple)]
    floating_holidays: list[KnownFloatingHoliday] = [cast(KnownFloatingHoliday, h) for h in holidays if isinstance(h, str)]

    skip_weekends = args["skip_weekends"]

    overall_direction = -1 if result_date < og_date else 1 if result_date > og_date else 0
    if log:
        if overall_direction < 0: print("Overall, the adjustment moved the date backwards")
        elif overall_direction > 0: print("Overall, the adjustment moved the date forwards")
        else: print("Overall, the adjustment did not change the date")

    prev_year = result_date.year
    @do_while
    def holiday_weekend_adjust() -> bool:
        nonlocal result_date
        nonlocal prev_year
        nonlocal floating_holidays

        prev_year = result_date.year

        current_floating_holiday = which_known_holiday(result_date.month, result_date.day, result_date.year, holiday_set=floating_holidays)

        should_skip_weekend = skip_weekends and result_date.weekday() >= 5
        should_skip_fixed_holiday = (result_date.month, result_date.day) in fixed_holidays
        should_skip_floating_holiday = current_floating_holiday is not None
        should_skip = should_skip_weekend or should_skip_fixed_holiday or should_skip_floating_holiday
        
        if log:
            if should_skip_weekend: print(f"Skipping weekend date {'backwards' if overall_direction < 0 else 'forwards'}: {result_date_str_notime()}")
            elif should_skip_fixed_holiday:
                print(f"Skipping holiday date {'backwards' if overall_direction < 0 else 'forwards'}: {result_date_str_notime()}")
            elif should_skip_floating_holiday:
                print(f"Skipping floating holiday {current_floating_holiday} {'backwards' if overall_direction < 0 else 'forwards'}: {result_date_str_notime()}")

        if should_skip:
            result_date += timedelta(days=(overall_direction if overall_direction != 0 else 1))  # If no overall direction, default to forward
            if log: print(f"New date: {result_date_str_notime()}")
            return True
        
        return False

    holiday_weekend_adjust()

    return result_date_str()