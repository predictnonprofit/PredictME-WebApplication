# -*- coding: utf-8 -*-#
from django import template
from termcolor import cprint

register = template.Library()


@register.filter
def get_is_seen(is_seen):
    is_seen_tag_code = ""

    if is_seen is True:
        is_seen_tag_code = """
            <span class="label label-lg label-success label-pill label-inline mr-2">
                Seen
            </span>
        """
    else:
        is_seen_tag_code = """
            <span class="label label-lg label-danger label-pill label-inline mr-2">
                Not seen
            </span>
        """
    return is_seen_tag_code.strip()


@register.filter
def get_status(crash_status):
    """
    CRASH_STATUS = (
        ("not_fixed", "Not Fixed"),
        ("fixed", "Fixed"),
        ("in_progress", "In Progress"),
    )
    """
    crash_status_tag_code = ""
    if crash_status == 'not_fixed':
        crash_status_tag_code = """
            <span class="label label-lg label-danger label-pill label-inline mr-2">
                Not Fixed
            </span>
            """
    elif crash_status == "in_progress":
        crash_status_tag_code = """
            <span class="label label-lg label-info label-pill label-inline mr-2">
                In Progress
            </span>
            """
    elif crash_status == "fixed":
        crash_status_tag_code = """
            <span class="label label-lg label-success label-pill label-inline mr-2">
                Fixed
            </span>
            """

    return crash_status_tag_code.strip()


@register.filter
def get_is_solved(is_solved):
    is_solved_tag_code = ""
    if is_solved is True:
        is_solved_tag_code = """
             <span class="label label-lg label-success label-pill label-inline mr-2">
                Yes
            </span>
        """
    else:
        is_solved_tag_code = """
             <span class="label label-lg label-danger label-pill label-inline mr-2">
                No
            </span>
        """
    return is_solved_tag_code.strip()
