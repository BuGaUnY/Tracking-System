from django import template
from datetime import datetime
from django.utils.dateformat import format

register = template.Library()

@register.filter
def date_th(value):
    try:
        # Format date as 'วันที่ DD เดือน MMMM พ.ศ. YYYY'
        year = value.year + 543  # Adjust to BE year
        month_names = {
            1: "มกราคม",
            2: "กุมภาพันธ์",
            3: "มีนาคม",
            4: "เมษายน",
            5: "พฤษภาคม",
            6: "มิถุนายน",
            7: "กรกฎาคม",
            8: "สิงหาคม",
            9: "กันยายน",
            10: "ตุลาคม",
            11: "พฤศจิกายน",
            12: "ธันวาคม"
        }
        month = month_names[value.month]
        day = value.strftime('%d')
        return f"{day} {month} {year}"
    except AttributeError:
        return "Invalid date"

    
@register.filter
def time_th(value):

    if not isinstance(value, (datetime, datetime.time)):
        raise ValueError("Invalid time format. Please provide a datetime or time object.")

    hour = str(value.hour).zfill(2)
    minute = str(value.minute).zfill(2)

    return f"{hour}:{minute}"


