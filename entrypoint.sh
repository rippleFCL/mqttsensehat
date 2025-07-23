#!/bin/bash

set -e

# Create group if it doesn't exist
if ! getent group "$GID" >/dev/null; then
    groupadd -g "$GID" sensehat
fi
# Create additional groups if they don't exist
if ! getent group 102 >/dev/null; then
    groupadd -g 102 input
fi
if ! getent group 993 >/dev/null; then
    groupadd -g 993 gpio
fi

if ! id -u sensehat >/dev/null 2>&1; then
    useradd -m -u "$UID" -g "$GID" sensehat
fi
# Add sensehat user to input and gpio groups if user exists
if id -u sensehat >/dev/null 2>&1; then
    usermod -aG input,gpio sensehat
fi
# Create user if it doesn't exist

# Run main.py as sensehat user
exec su -s /bin/bash -c "python3 main.py" sensehat
