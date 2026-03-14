"""Custom exceptions for iban-tools."""


class IbanToolsError(Exception):
    """Base exception for all iban-tools errors."""
    pass


class InvalidIbanError(IbanToolsError):
    """Raised when an IBAN fails validation."""

    def __init__(self, iban: str, reason: str = "Invalid IBAN"):
        self.iban = iban
        self.reason = reason
        super().__init__(f"{reason}: {iban}")


class UnsupportedCountryError(IbanToolsError):
    """Raised when a country code is not supported."""

    def __init__(self, country_code: str):
        self.country_code = country_code
        super().__init__(f"Unsupported country code: {country_code}")


class BicNotFoundError(IbanToolsError):
    """Raised when a BIC cannot be found for a given IBAN."""

    def __init__(self, iban: str, bank_code: str):
        self.iban = iban
        self.bank_code = bank_code
        super().__init__(
            f"BIC not found for bank code '{bank_code}' from IBAN: {iban}"
        )
