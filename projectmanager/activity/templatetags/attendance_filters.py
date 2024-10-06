from django import template

register = template.Library()

@register.filter
def get_activity_status(reports, activity_name):
    for report in reports:
        if report.att_name == activity_name:
            return report.status
    return "-"  # Default value if not found
