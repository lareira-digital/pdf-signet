import os

# Minimum Python version required
REQUIRED_PYTHON = (3, 13)

# Current version of the service, may not match with pyproject.toml
VERSION = os.getenv("PDF_SIGNET_VERSION", "0.0.0")

# DEBUG flag, setting this to true only makes the service more verbose,
# the behaviour is the save in debug and production mode
DEBUG = os.getenv("PDF_SIGNET_DEBUG", True)

# List of authorized hosts, separated by commas. Example: localhost,whatever,*
AUTHORIZED_HOSTS = os.getenv("PDF_SIGNET_AUTHORIZED_HOSTS", "*").split(",")

# Maximum size the PDF can have, by default 20MB. Measured in bytes.
MAX_UPLOAD_SIZE = int(
    os.getenv("PDF_SIGNET_MAX_UPLOAD_SIZE", "20971520")
)