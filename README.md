# Enexis outage

This custom integration will scrape the Enexis website on your zipcode to see if something in their power network blew up :).
One could argue if Home assistant will be powered when this happens. but I have encountered the issue with on of the three phases (230V) being cut, which will render 1/3 of your house powerless. 

## How it works

It scrapes the website of Enexis (one of the Dutch power grid maintainers) on your zipcode to see if there is a failure. At the moment the scraper runs every 30 minutes. A binary sensor binary_sensor.enexis_outage_1234AB is created and will be in an off state (no failures) or on state (failure in/around your zipcode). You can then build an automation that will notify you, provided Home Assistant is still able to run and access the Internet.

## Installation.

Put the enexis_outage in your custom_components folder in Homeassistant. I run under their supervisor install so in my case it looks like:

```
/config/custom_components/enexis_outage
```

Restart HA and then go to your Integrations and search for Enexis. Add your zipcode and save. Then build automations as you see fit.

## Notes

- This only works for Enexis and you have to be in Enexis servicing area. In NL there are 3 major power grid maintainers, check https://www.mijnaansluiting.nl/netbeheerders if you are unsure.
- This is not offically supported by Home Assistant. Use at your own risk.

