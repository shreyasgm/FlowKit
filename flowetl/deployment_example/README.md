## FlowETL sample deployment

This directory contains the files necessary to do an example deployment of FlowETL,
which will ingest sample calls data from an external PostgreSQL database and sample
SMS data from a CSV file.

The remainder of this README describes the steps to set up this deployment and run
the ingestion process. For the initial steps of building the relevant docker images,
you need a local clone of the FlowKit repository. For simplicity, the steps below
assume that you are running them from within this local clone, inside the
directory `flowetl/deployment_example/`.

In a production deployment, you would simply upload the docker images directly to the
server, or pull them there if the server has internet connection. However, for development
and testing it is useful to build the images locally, which is the method described here.
Note that some other parts of the setup - e.g. using a docker swarm or setting up a
local registry - are not strictly needed for a local example deployment, but we describe
them here in order to mimic a production setup as closely as possible.


### Set up a docker stack with FlowDB, FlowETL and an external PostgreSQL database

First, set relevant environment variables. Most of them are pre-defined in `defaults.env`,
but we need to set the path to the local clone of the FlowKit repo manually.

```bash
set -a && source ./defaults.env && set +a
export LOCAL_FLOWKIT_REPO=$(pwd)/../..
```

Make the machine you're working on a docker swarm manager.
```
docker swarm init

# Note: if the previous command fails, use the following one with the public IP address of this machine
#docker swarm init --advertise-addr=<ip_address_of_vm>
```

Start a local docker registry as a service on the swarm.
```
docker service create --name registry --publish published=5000,target=5000 registry:2
```

You can use the following command to verify that the registry is working (this should simply print '{}').
```
curl -w '\n' http://127.0.0.1:5000/v2/
```

Build FlowDB and FlowETL.
```
make build-flowdb        # this may take ~3-4 minutes
make build-flowetl       # this is quick (~30s)
```

For testing purposes, we also build a separate PostgreSQL database (`ingestion_db`)
which includes some sample data and which will serve as the "external" database
from which we ingest data into FlowDB.
```
make build-ingestion_db  # this is quick (~10s)
```

Next, push the three docker images which we just built to the local registry.
```
make push-to-local-registry  # this may take a couple of minutes the first time around
```

Finally, deploy the docker stack.
```
make deploy-stack
```

After a few seconds, everything should be up and running.
You can use `docker service ls` to verify this.
```
$ docker service ls
ID                  NAME                        MODE                REPLICAS            IMAGE                                PORTS
x2ta1p814rm9        flowetl_test_flowdb         replicated          1/1                 127.0.0.1:5000/flowdb:latest         *:12000->5432/tcp
tt2fsck1h3ib        flowetl_test_flowetl        replicated          1/1                 127.0.0.1:5000/flowetl:latest        *:8080->8080/tcp
ucrf2cnm84f1        flowetl_test_flowetl_db     replicated          1/1                 postgres:11                          *:5433->5432/tcp
xcygfxylfrn8        flowetl_test_ingestion_db   replicated          1/1                 127.0.0.1:5000/ingestion_db:latest   *:5444->5432/tcp
s5xo9hth5u0z        registry                    replicated          1/1                 registry:2                           *:5000->5000/tcp
```

You can connect to the databases `flowdb`, `ingestion_db` or `flowetl_db` (= the database
which the Airflow instance in `flowetl` uses internally) by running the following convenience
Makefile commands. (Of course, regular `psql` connection commands work as well.)
```bash
make connect-flowdb
make connect-ingestion_db
make connect-flowetl_db
```

If you want to shut down the docker services in the stack, use the following command.
```bash
make shut-down-stack-without-purging-volumes
```
This calls the script `shut_down_docker_stack.sh`, which ensures that any networks set up by docker
will be removed as well (which otherwise can be a bit flaky; see references in the script for details).
In rare cases this still fails, but a restart of the docker daemon should fix it and remove any
spurious networks. Note that this command retains the docker volumes used by the databases so that
when you bring up the stack again the data is still available (including bookkeeping data about
previous Airflow runs).


_Note:_ there is a convenience Makefile target to run the build and deploy commands above (after creating
the docker registry) in a single step:
```bash
make build-and-deploy
```
This is useful if you make changes to the source code, in which cae you need to re-build the docker images
for these changes to be picked up.


### Sample data in IngestionDB

The `ingestion_db` instance contains sample data in the table `events.sample` (generated by the
scripts `ingestion_db/sql/create_sample_table.sql` and `ingestion_db/sql/populate_sample_table.sql`).


### Create a foreign data wrapper to connect FlowDB to IngestionDB

Run the following from within `flowdb` (you can connect to flowdb by running `make connect-flowdb`).
```
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE SERVER IF NOT EXISTS ingestion_db_server FOREIGN DATA WRAPPER postgres_fdw OPTIONS (host 'ingestion_db', port '5432', dbname 'ingestion_db');
CREATE USER MAPPING IF NOT EXISTS FOR flowdb SERVER ingestion_db_server OPTIONS (user 'ingestion_db', password 'etletl');

CREATE FOREIGN TABLE sample_data_fdw (
        event_time TIMESTAMPTZ,
        msisdn TEXT,
        cell_id TEXT
    )
    SERVER ingestion_db_server
    OPTIONS (schema_name 'events', table_name 'sample');
```


### Run Airflow

At this point you have the following:

- An instance of `ingestion_db` with some sample data in the table `events.sample`
- An instance of `flowdb` with a foreign table called `sample_data_fdw` which wraps the `events.sample` table in `ingestion_db`.


Let's start the ingestion DAGs via the Airflow web interface.

- Navigate to http://localhost:8080, which should present you with the Airflow web interface.
- Activate the `etl_sensor`, `etl_calls` and `etl_sms` DAGs (by clicking on the "Off" buttons next to them so that they show "On" instead).
- Click on the "Trigger Dag" button for the `etl_sensor` DAG. (This is the leftmost arrow button in the "Links" column.)
   - Airflow will present you with a dialog, asking "Are you sure you want to run 'etl_sensor' now?".
   - Click "OK" to confirm this.
- Airflow will now run the `etl_sensor` DAG, which will look for any unprocessed dates,
  and trigger runs of the `etl_calls` and `etl_sms` DAGs for any unprocessed date it finds.
  
  This may take a minute or so - in order to see the progress, either reload your browser
  page, or click the "Refresh" button on one of the DAGs in the Airflow UI. (This is the
  button with the two circular arrows next to the button with the red cross.)

  You can also click on `etl_calls` or `etl_sms` in the "DAG" column (or alternativey navigate
  to http://localhost:8080/admin/airflow/tree?dag_id=etl_calls or http://localhost:8080/admin/airflow/tree?dag_id=etl_sms)
  to see a grid of squares indicating the various ingestion stages for each day of data found.

If all goes well, after a little while all the DAGs will have been completed and the data
will have been ingested into the `events.calls` and `events.sms` table. If you click on the
`etl_calls`/`etl_sms` DAGs you should see a bunch of green squares for the successfully
completed tasks for each ingestion date.

The result in `flowdb` should look something like this:
```
$ make connect-flowdb
psql "postgresql://flowdb:flowflow@127.0.0.1:11000/flowdb"
psql (11.1, server 11.4 (Debian 11.4-1.pgdg90+1))
Type "help" for help.

flowdb=# SELECT date, COUNT(*) FROM (SELECT datetime::date as date FROM events.calls) _ GROUP BY date ORDER BY DATE;
    date    | count
------------+-------
 2019-07-04 | 46446
 2019-07-05 | 86400
 2019-07-06 | 86400
 2019-07-07 | 86400
 2019-07-08 | 86400
 2019-07-09 | 86400
 2019-07-10 | 86400
 2019-07-11 | 86400
 2019-07-12 | 86400
 2019-07-13 | 86400
 2019-07-14 | 86400
 2019-07-15 | 86400
 2019-07-16 |  3155
(13 rows)

flowdb=# SELECT date, COUNT(*) FROM (SELECT datetime::date as date FROM events.sms) _ GROUP BY date ORDER BY DATE;
    date    | count
------------+-------
 2019-01-01 |   100
 2019-01-02 |   120
 (1 row)
```