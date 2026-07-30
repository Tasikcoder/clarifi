import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# Detect SPCS environment once
SPCS_TOKEN_PATH = "/snowflake/session/token"
IS_SPCS = os.path.exists(SPCS_TOKEN_PATH)


def get_snowflake_config() -> dict:
    """Build Snowflake connection config. Re-reads token on every call for SPCS freshness."""
    config = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT", "YHNOMRY-UW19292"),
        "database": os.getenv("SNOWFLAKE_DATABASE", "CLARIFI"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", "CLAIMS"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    }

    if IS_SPCS:
        config["authenticator"] = "oauth"
        config["token"] = open(SPCS_TOKEN_PATH).read()
        config["host"] = os.getenv("SNOWFLAKE_HOST", "")
    else:
        config["user"] = os.getenv("SNOWFLAKE_USER", "slametsantoso")
        config["password"] = os.getenv("SNOWFLAKE_PASSWORD", "")

    return config
