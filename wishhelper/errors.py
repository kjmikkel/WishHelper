"""Exception hierarchy for the Qt-free core."""


class WishHelperError(Exception):
    """Base class for all WishHelper errors."""


class StorageError(WishHelperError):
    """Raised when a wishlist file cannot be read, parsed, or written."""


class LegacyFormatError(StorageError):
    """Raised when an old-format file cannot be converted to the current model."""


class SettingsError(WishHelperError):
    """Raised when the settings file cannot be read or written."""
