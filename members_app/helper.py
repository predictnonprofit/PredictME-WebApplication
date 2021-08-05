def calculate_records_left_percentage(data_obj, data_session):
    """
    this function will take data object, and data session to calculate how many left of records used
    by get the percentage of the records that left and not used.
    @return this will return integer
    """
    try:
        allowed_records_count = data_obj.allowed_records_count
        used_records = data_session.all_records_count
        total_used = used_records / allowed_records_count
        return round(total_used * 100)
    except AttributeError:
        return 0
