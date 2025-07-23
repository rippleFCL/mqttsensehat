#!/bin/bash

set -e

# Create group if it doesn't exist
if ! getent group "$SENSEHAT_GID" >/dev/null; then
    groupadd -g "$SENSEHAT_GID" sensehat
fi

# Create user if it doesn't exist
if ! id -u sensehat >/dev/null 2>&1; then
    useradd -m -u "$SENSEHAT_UID" -g "$SENSEHAT_GID" sensehat
fi

# Run main.py as sensehat user
exec su -s /bin/bash -c "python3 main.py" sensehat
