
# Django Kenyan Phone Fields

A collection of custom Django model fields for Kenyan phone numbers. Currently supports:

- **SafaricomPhoneField**: Validates only known Safaricom prefixes.  
- **AirtelPhoneField**: Validates only known Airtel prefixes.  
- **KenyanPhoneField**: Validates any Kenyan mobile number starting with `07xx...` or `01xx...`.

Each field normalizes the phone number to a **`254XXXXXXXXX`** format for storage in the database.

## Installation

1. Copy **`kenyan_phone_fields.py`** into one of your Django apps (or a utility folder) within your project.
2. Ensure that app or folder is on your Python path (which it will be if it's part of a Django app).


## Usage

In your `models.py`:

```python
from django.db import models
from path.to.kenyan_phone_fields import (
    SafaricomPhoneField,
    AirtelPhoneField,
    KenyanPhoneField
)

class YourModel(models.Model):
    safaricom_number = SafaricomPhoneField(blank=True, null=True)
    airtel_number = AirtelPhoneField(blank=True, null=True)
    any_kenyan_number = KenyanPhoneField(blank=True, null=True)
```

### Validation Behavior

1. **SafaricomPhoneField**:
   - Checks whether the user input matches known Safaricom prefixes (e.g. `070x`, `071x`, `072x`, `074x`, `079x`, `011x`, etc.).
   - Raises a `ValidationError` if not matched.

2. **AirtelPhoneField**:
   - Checks against Airtel prefixes (`073x`, `075x`, `078x`, `010x`, etc.).
   - Raises a `ValidationError` if not matched.

3. **KenyanPhoneField**:
   - Uses a regex for any Kenyan mobile number starting with `07` or `01`, allowing an optional `+254` or leading `0`.
   - Raises a `ValidationError` if not matched.

All fields will store the normalized version (`254XXXXXXXXX`) in the database.

## Contributing

- **New or changed prefixes**: Safaricom, Airtel, Telkom, etc., occasionally introduce new prefixes. If you find any missing or incorrect ranges, please open an issue or submit a pull request with updates to the prefix lists or validation logic.
- **Bug fixes / Enhancements**: PRs are welcome! If you find a bug or have an improvement, submit a PR with clear details and test cases.

## License

[MIT License](LICENSE)
