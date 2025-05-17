"""Enexis Outage Status integration."""
import asyncio
import logging
from datetime import timedelta
import aiohttp
import async_timeout
from bs4 import BeautifulSoup

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_ZIPCODE,
    DEFAULT_SCAN_INTERVAL,
    BASE_URL,
    NO_OUTAGE_TEXT,
    SERVICE_CHECK_NOW,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Enexis Outage Status from a config entry."""
    zipcode = entry.data[CONF_ZIPCODE]
    
    session = async_get_clientsession(hass)
    coordinator = EnexisOutageCoordinator(
        hass,
        _LOGGER,
        zipcode=zipcode,
        session=session,
        update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register service to manually check for outages
    async def handle_check_now(call: ServiceCall) -> None:
        """Handle the service call to check for outages right now."""
        _LOGGER.debug("Manual check for outages triggered")
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN, SERVICE_CHECK_NOW, handle_check_now, schema=vol.Schema({})
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class EnexisOutageCoordinator(DataUpdateCoordinator):
    """Class to manage fetching outage data from the Enexis website."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        zipcode: str,
        session: aiohttp.ClientSession,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.zipcode = zipcode
        self.session = session
        self.url = BASE_URL.format(zipcode)

    async def _async_update_data(self):
        """Fetch data from the Enexis website."""
        try:
            async with async_timeout.timeout(30):
                response = await self.session.get(self.url)
                response.raise_for_status()
                html = await response.text()

                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract main content
                main_content = soup.find('main')
                if not main_content:
                    _LOGGER.warning("Could not find main content on the page")
                    return {"outage": False, "message": "Error: Could not parse page"}
                
                # Look for outage message
                page_text = main_content.get_text()
                
                # Check for the "no outage" message
                if NO_OUTAGE_TEXT in page_text:
                    return {"outage": False, "message": NO_OUTAGE_TEXT}
                
                # If we didn't find the "no outage" message, try to extract the outage description
                outage_message = f"Storing bekend rondom {self.zipcode}"
                
                # Look for more specific outage information
                outage_details = ""
                details_section = main_content.find('div', class_='detail-storing')
                if details_section:
                    outage_details = details_section.get_text().strip()
                
                if outage_details:
                    outage_message += f": {outage_details}"
                
                return {"outage": True, "message": outage_message}
                
        except asyncio.TimeoutError:
            raise UpdateFailed("Timeout fetching outage data")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching outage data: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")
