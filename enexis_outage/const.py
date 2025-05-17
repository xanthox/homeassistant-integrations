"""Constants for the Enexis Outage Status integration."""

DOMAIN = "enexis_outage"

# Configuration constants
CONF_ZIPCODE = "zipcode"
DEFAULT_SCAN_INTERVAL = 30  # minutes

# Service constants
SERVICE_CHECK_NOW = "check_now"

# URL format
BASE_URL = "https://www.enexis.nl/storingen-en-onderhoud/{}"

# Text indicators
NO_OUTAGE_TEXT = "Geen storingen bekend"
