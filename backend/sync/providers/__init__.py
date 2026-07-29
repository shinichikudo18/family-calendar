from .microsoft import MicrosoftCalendarEngine
from .google import GoogleCalendarEngine

PROVIDERS = {
    'microsoft': MicrosoftCalendarEngine,
    'google': GoogleCalendarEngine,
}
