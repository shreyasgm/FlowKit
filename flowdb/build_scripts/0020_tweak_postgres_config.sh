#!/bin/sh
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

set -euo pipefail

#
#  Generates config file using the configurate.py script
#  and adds it to the PostgreSQL general configuration.
#

# Allows WAL to be skipped for CREATE TABLE & CLUSTER
# we configure this in the autogenerated config anyway,
# but nice to have it off from the start for the benefit
# of the testdata containers for increased performance
# during startup, which is why we add it here to the main
# config as well.
echo "---------------------------------------------------------"
echo " * Applying custom WAL settings and restarting postgres. "
echo "---------------------------------------------------------"

echo "wal_level='minimal'" >> /var/lib/postgresql/data/postgresql.conf
echo "max_wal_senders = 0" >> /var/lib/postgresql/data/postgresql.conf
pg_ctl -D "$PGDATA" \
       -o "-c listen_addresses=''" \
		-w restart

#
#  Fill the template values in 'pg_config_template.conf' with custom
#  configuration settings for the database, write it to its intended
#  location at /var/lib/postgresql/data/postgresql.configurator.conf,
#  and add a line to the main postgres configuration file at
#  /var/lib/postgresql/data/postgresql.conf to include it.
#
#  Note that we cannot write this configuration file in the
#  Dockerfile directly because the FlowDB docker container mounts
#  an external volume at /var/lib/postgresql/data/ so any files
#  copied to this location will be hidden and the config changes
#  won't take effect (and also we want to be able to dynamically
#  derive certain settings when the docker container starts up).

python3 /docker-entrypoint-initdb.d/configurate.py
echo "include 'postgresql.configurator.conf'" >> /var/lib/postgresql/data/postgresql.conf
