from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Hold all the configuration properties of the app, not only the ones related to Atoti.

    See https://pydantic-docs.helpmanual.io/usage/settings/.
    """

    model_config = SettingsConfigDict(frozen=True)

    check_mapping_lookups: bool = __debug__

    data_refresh_period: float | None = None
    """How often the station status data should be refreshed.

    If ``None``, only local data will be used: no requests will be made to external APIs.
    """

    # The $PORT environment variable is used by most PaaS to indicate the port the app server should bind to.
    port: int = 9090
