import re
from ipware import get_client_ip

REGEX_PATTERS = {
    "NAME": re.compile(r"^(?=.{1,40}$)[a-zA-Z]+(?:[-'\s][a-zA-Z]+)*$", re.IGNORECASE),  # full name
    "PHONE": re.compile(r"([+(\d]{1})(([\d+() -.]){5,16})([+(\d]{1})"),  # phone with country code
    "EMAIL": re.compile(r"^([0-9a-zA-Z].*?@([0-9a-zA-Z].*\.\w{2,4}))$", re.IGNORECASE),  # email address
    "ALPHNUM": re.compile(r"^[A-Za-z0-9\s]+[A-Za-z0-9\s]+$(\.0-9+)?", re.IGNORECASE),  # Alphanumeric with Spaces
    "ZIP": re.compile(r"[0-9]{5}(-[0-9]{4})?", re.IGNORECASE),  # zip code pattern
    "URL": re.compile(r"^(https?:\/\/)?([\da-z\.-]+\.[a-z\.]{2,6}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?$",
                      re.IGNORECASE),  # URL pattern
    "CITY": re.compile(r"^[A-Za-z]+(\s[A-Za-z]+)?\s*,*\s*[A-Za-z]+(\s[A-Za-z]+){1,25}?\s*$", re.IGNORECASE),
    # city name pattern
    "STREET_ADDRESS": re.compile(r"^([a-zA-z0-9/\\''(),\s]{2,255})$"),
}


def input_required(value):
    """Validate if value is empty or not

            Args:
                value: The Name parameter
            Returns:
                The return value. True if not empty, False otherwise.

            """
    if value == "" or value is None:
        return False
    else:
        return True


def validate_name(name):
    """Validate Name Function

        Args:
            name: The Name parameter
        Returns:
            The return value. True for valid name, False otherwise.

        """
    if REGEX_PATTERS['NAME'].search(name):
        return True
    else:
        return False


def validate_street_address(address):
    """Validate Street Address Function

        Args:
            address: The Name parameter
        Returns:
            The return value. True for valid name, False otherwise.

        """
    if REGEX_PATTERS['STREET_ADDRESS'].search(address):
        return True
    else:
        return False


def validate_email(email):
    """Validate Email Function

        Args:
            email: The Email Address parameter
        Returns:
            The return value. True for valid email, False otherwise.

        """
    if REGEX_PATTERS['EMAIL'].search(email):
        return True
    else:
        return False


def validate_phone(phone):
    """Validate Phone Function

        Args:
            phone: The phone number
        Returns:
            The return value. True for valid phone, False otherwise.

        """
    if REGEX_PATTERS['PHONE'].search(phone):
        return True
    else:
        return False


def validate_alphnum(text):
    """Validate alphanumeric Function

        Args:
            text: The text
        Returns:
            The return value. True for valid alphanumeric, False otherwise.

        """
    if REGEX_PATTERS['ALPHNUM'].search(text):
        return True
    else:
        return False


def validate_zip(zip):
    """Validate zip Function

        Args:
            zip: The zip
        Returns:
            The return value. True for valid zip, False otherwise.

        """
    if REGEX_PATTERS['ZIP'].search(zip):
        return True
    else:
        return False


def validate_url(url):
    """Validate url Function

        Args:
            url: The url
        Returns:
            The return value. True for valid url, False otherwise.

        """
    if REGEX_PATTERS['URL'].search(url):
        return True
    else:
        return False


def validate_city(city):
    """Validate city Function

        Args:
            city: The city name
        Returns:
            The return value. True for valid city, False otherwise.

        """
    if REGEX_PATTERS['CITY'].search(city):
        return True
    else:
        return False


def validate_password(password: str):
    password = password.strip()
    error_and_bool = []  # first True|False, second the error msg
    """will validate the password to match the required conditions

    Arguments:
        password {[str]} -- password will validate
    
    Contain at least six characters
    Include at least one letter and one number
    Not repeat the same character more than two times in a row
    Not include white spaces
    """
    all_chars = []
    for ch in password:
        all_chars.append(ch)

    if len(all_chars) < 6:
        error_and_bool = [False, "Password is short, Minimum length 7 characters!"]
        return error_and_bool


def get_member_ip_address(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        # Unable to get the client's IP address
        return "Unable to get the client's IP address"
    else:
        # We got the client's IP address
        if is_routable:
            # The client's IP address is publicly routable on the Internet
            return client_ip
        else:
            # The client's IP address is private
            return f"{client_ip} - private address"
