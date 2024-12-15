from homeassistant.components.number import NumberEntity
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class CustomNumber(NumberEntity):
    """Custom number entity for multiple hubs."""

    def __init__(self, name, hub_name, coordinator, min_value, max_value, step, unit, initial_value=None):
        """Initialize the number entity."""
        self._name = name
        self.hub_name = hub_name
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        self._unit = unit
        self._value = initial_value or min_value
        self.coordinator = coordinator
        self._unique_id = f"{DOMAIN}_{hub_name}_{name.lower().replace(' ', '_')}"

    @property
    def unique_id(self):
        """Return the unique ID for this entity."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def native_min_value(self):
        return self._min_value

    @property
    def native_max_value(self):
        return self._max_value

    @property
    def native_step(self):
        return self._step

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def native_value(self):
        """Return the current value of the number."""
        return self._value

    @property
    def device_info(self):
        """Return device information to link this entity to a device."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": f"Device for {self._name}",
            "model": "Number Device",
            "manufacturer": "OpenGrowBox",
            "suggested_area": self.hub_name,  # Optional: Gibt einen Hinweis für den Bereich
        }

    async def async_set_native_value(self, value: float):
        """Set a new value."""
        if self._min_value <= value <= self._max_value:
            self._value = value
            self.async_write_ha_state()
            _LOGGER.info(f"Number '{self._name}' set to {value}")
        else:
            _LOGGER.warning(f"Value {value} out of range for '{self._name}'")

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create number entities
    numbers = [
        CustomNumber(f"{coordinator.hub_name}_LeafTemp", coordinator.hub_name, coordinator,
                min_value=0.0, max_value=5.0, step=0.1, unit="°C", initial_value=2.0),
        CustomNumber(f"{coordinator.hub_name}_VPDTarget", coordinator.hub_name, coordinator,
                    min_value=0.0, max_value=5.0, step=0.1, unit="°C", initial_value=0.0),
        CustomNumber(f"{coordinator.hub_name}_TargetTemperature", coordinator.hub_name, coordinator,
                     min_value=10.0, max_value=35.0, step=0.1, unit="°C", initial_value=20.0),
        CustomNumber(f"{coordinator.hub_name}_TargetHumidity", coordinator.hub_name, coordinator,
                     min_value=20.0, max_value=80.0, step=1.0, unit="%", initial_value=60.0),
    ]

    if "numbers" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["numbers"] = []

    hass.data[DOMAIN]["numbers"].extend(numbers)
    async_add_entities(numbers)