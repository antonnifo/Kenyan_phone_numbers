# kenyan_phone_fields.py

import re
from django.core.exceptions import ValidationError
from django.db import models

###############################################################################
# 1. SafaricomPhoneField
###############################################################################

def validate_safaricom_number(value):
    """
    Validator for Safaricom numbers:
      - Allows blank or None.
      - Checks prefix against known Safaricom prefixes.
      - Expects 9 digits after stripping +254 / 254 / 0.
    """
    if not value:
        return  # allow blank/None

    safaricom_prefixes = [
        '0700', '0701', '0702', '0703', '0704', '0705', '0706', '0707', '0708', '0709',
        '0710', '0711', '0712', '0713', '0714', '0715', '0716', '0717', '0718', '0719',
        '0720', '0721', '0722', '0723', '0724', '0725', '0726', '0727', '0728', '0729',
        '0740', '0741', '0742', '0743', '0745', '0746', '0748',
        '0757', '0758', '0759',
        '0768', '0769',
        '0790', '0791', '0792', '0793', '0794', '0795', '0796', '0797', '0798', '0799',
        '0110', '0111', '0112', '0113', '0114', '0115',
    ]

    # Normalize for validation
    normalized = value
    if normalized.startswith('+254'):
        normalized = normalized[4:]
    elif normalized.startswith('254'):
        normalized = normalized[3:]
    elif normalized.startswith('0'):
        normalized = normalized[1:]

    # Check prefix (note: compare normalized to prefix[1:])
    if not any(normalized.startswith(prefix[1:]) for prefix in safaricom_prefixes):
        raise ValidationError(
            f"{value} is not a valid Safaricom prefix."
        )

    if len(normalized) != 9:
        raise ValidationError(
            f"{value} must be 9 digits long after removing country code."
        )


class SafaricomPhoneField(models.CharField):
    """
    Custom Django field for storing Safaricom phone numbers.
    - Validates against Safaricom prefixes only.
    - Normalizes to '254XXXXXXXXX' in the database.
    """
    default_validators = [validate_safaricom_number]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 12  # '254' + 9 digits
        # Optionally set default blank=True, null=True if you want
        # kwargs.setdefault('blank', True)
        # kwargs.setdefault('null', True)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return value

        # Normalize to '254'
        if value.startswith('+254'):
            return '254' + value[4:]
        elif value.startswith('0'):
            return '254' + value[1:]
        elif not value.startswith('254'):
            return '254' + value
        return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value

        if value.startswith('+254'):
            return '254' + value[4:]
        elif value.startswith('0'):
            return '254' + value[1:]
        elif not value.startswith('254'):
            return '254' + value
        return value


###############################################################################
# 2. AirtelPhoneField
###############################################################################

def validate_airtel_number(value):
    """
    Validator for Airtel Kenya numbers:
      - Allows blank or None.
      - Checks prefix against known Airtel prefixes.
      - Expects 9 digits after stripping +254 / 254 / 0.
    """
    if not value:
        return  # allow blank/None

    airtel_prefixes = [
        # 073x
        '0730', '0731', '0732', '0733', '0734', '0735', '0736', '0737', '0738', '0739',
        # 075x
        '0750', '0751', '0752', '0753', '0754', '0755', '0756',
        # 078x
        '0780', '0781', '0782', '0783', '0784', '0785', '0786', '0787', '0788', '0789',
        # 010x
        '0100', '0101', '0102', '0103', '0104', '0105', '0106', '0107', '0108', '0109',
    ]

    # Normalize
    normalized = value
    if normalized.startswith('+254'):
        normalized = normalized[4:]
    elif normalized.startswith('254'):
        normalized = normalized[3:]
    elif normalized.startswith('0'):
        normalized = normalized[1:]

    # Check prefix
    if not any(normalized.startswith(prefix[1:]) for prefix in airtel_prefixes):
        raise ValidationError(
            f"{value} is not a valid Airtel Kenya prefix."
        )

    if len(normalized) != 9:
        raise ValidationError(
            f"{value} must be 9 digits long after removing country code."
        )


class AirtelPhoneField(models.CharField):
    """
    Custom Django field for storing Airtel Kenya phone numbers.
    - Validates Airtel prefixes only.
    - Normalizes to '254XXXXXXXXX' in DB.
    """
    default_validators = [validate_airtel_number]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 12  # '254' + 9 digits
        # kwargs.setdefault('blank', True)
        # kwargs.setdefault('null', True)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return value

        if value.startswith('+254'):
            return '254' + value[4:]
        elif value.startswith('0'):
            return '254' + value[1:]
        elif not value.startswith('254'):
            return '254' + value
        return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value

        if value.startswith('+254'):
            return '254' + value[4:]
        elif value.startswith('0'):
            return '254' + value[1:]
        elif not value.startswith('254'):
            return '254' + value
        return value


###############################################################################
# 3. KenyanPhoneField (generic for mobile: 07... or 01...)
###############################################################################

KENYAN_MOBILE_REGEX = re.compile(
    r'^(?:\+?254|0)(7\d{8}|1\d{8})$'
    # Explanation:
    # - ^ start of string
    # - (?:\+?254|0) => either +254 or 0
    # - (7\d{8}|1\d{8}) => after that prefix, either '7' + 8 digits or '1' + 8 digits
    # - $ end of string
)


def validate_kenyan_number(value):
    """
    Validator for a generic Kenyan mobile number (07xx... or 01xx...).
      - Allows blank/None.
      - Uses a simple regex to match 07XXXXXXXX or 01XXXXXXXX, with optional +254 or 0 in front.
    """
    if not value:
        return  # allow blank/None

    if not KENYAN_MOBILE_REGEX.match(value):
        raise ValidationError(
            f"{value} is not a valid Kenyan mobile number format."
        )


class KenyanPhoneField(models.CharField):
    """
    A Django field that accepts any Kenyan mobile number matching 07xx... or 01xx...
    Normalizes them to '2547xxxxxxxx' or '2541xxxxxxxx'.
    """
    default_validators = [validate_kenyan_number]

    def __init__(self, *args, **kwargs):
        # '254' + 9 or 10 digits => often 12 or 13 max length
        kwargs['max_length'] = 13
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return value

        # Remove any leading '+'
        if value.startswith('+'):
            value = value[1:]

        # If it starts with 254, assume it's already normalized.
        if value.startswith('254'):
            return value
        elif value.startswith('0'):
            # '07...' or '01...' => remove '0', prepend '254'
            return '254' + value[1:]
        else:
            # If it doesn't start with '0' or '254', forcibly prepend '254'
            # but typically you won't hit this if your regex enforces correct format
            return '254' + value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value

        if value.startswith('+254'):
            return '254' + value[4:]
        elif value.startswith('0'):
            return '254' + value[1:]
        elif not value.startswith('254'):
            return '254' + value
        return value
