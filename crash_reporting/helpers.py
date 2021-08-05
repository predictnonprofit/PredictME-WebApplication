# -*- coding: utf-8 -*-#
# this file will create a new bug report when it happen

"""
    ASGI Request Methods
    ['COOKIES', 'FILES', 'GET', 'META', 'POST', '_cached_user', '_content_length', '_current_scheme_host', '_encoding',
    '_get_files', '_get_full_path', '_get_post', '_get_raw_host', '_get_scheme', '_initialize_handlers',
    '_load_post_and_files', '_mark_post_parse_error', '_messages', '_post_parse_error', '_read_started',
    '_set_content_type_params', '_set_post', '_stream', '_upload_handlers', 'accepted_types', 'accepts', 'body',
    'body_receive_timeout', 'build_absolute_uri', 'close', 'content_params', 'content_type', 'csrf_processing_done',
    'encoding', 'get_full_path', 'get_full_path_info', 'get_host', 'get_port', 'get_raw_uri', 'get_signed_cookie',
    'headers', 'is_ajax', 'is_secure', 'method', 'parse_file_upload', 'path', 'path_info', 'read', 'readline',
    'readlines', 'resolver_match', 'scheme', 'scope', 'script_name', 'session', 'upload_handlers', 'user']
"""
from channels.http import AsgiRequest


def create_crash_report(request: AsgiRequest):
    """
    This function will create a new crash report when it happen
    """
    pass
