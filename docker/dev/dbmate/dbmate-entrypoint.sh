#!/bin/sh
set -e

# Wait for the database to be ready
dbmate wait

# Run dbmate commands
dbmate up

# Keep the container running
tail -f /dev/null