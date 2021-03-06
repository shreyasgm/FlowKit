# Changelog

All notable changes to FlowKit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

## [1.1.1]

### Added
- Added a worked example to demonstrate using joined spatial aggregate queries. [#1938](https://github.com/Flowminder/FlowKit/issues/1938)

## [1.1.0]

### Changed
- `Connection.available_dates` is now a property and returns results based on the `etl.etl_records` table. [#1873](https://github.com/Flowminder/FlowKit/issues/1873)

### Fixed
- Fixed the run action blocking the FlowMachine server in some scenarios. [#1256](https://github.com/Flowminder/FlowKit/issues/1256)

### Removed
- Removed `tables` and `columns` methods from the `Connection` class in FlowMachine
- Removed the `inspector` attribute from the `Connection` class in FlowMachine


## [1.0.0]

### Added
- FlowMachine now periodically prunes the cache to below the permitted cache size. [#1307](https://github.com/Flowminder/FlowKit/issues/1307)
  The frequency of this pruning is configurable using the `FLOWMACHINE_CACHE_PRUNING_FREQUENCY` environment variable to Flowmachine, and queries are excluded from being removed by the automatic shrinker based on the `cache_protected_period` config key within FlowDB.
- FlowDB now includes Paul Ramsey's [OGR foreign data wrapper](https://github.com/pramsey/pgsql-ogr-fdw), for easy loading of GIS data. [#1512](https://github.com/Flowminder/FlowKit/issues/1512)
- FlowETL now allows all configuration options to be set using docker secrets. [#1515](https://github.com/Flowminder/FlowKit/issues/1515)
- Added a new component, AutoFlow, to automate running Jupyter notebooks when new data is added to FlowDB. [#1570](https://github.com/Flowminder/FlowKit/issues/1570)
- `FLOWETL_INTEGRATION_TESTS_SAVE_AIRFLOW_LOGS` environment variable added to allow copying the Airflow logs in FlowETL integration tests into the /mounts/logs directory for debugging. [#1019](https://github.com/Flowminder/FlowKit/issues/1019)
- Added new `IterativeMedianFilter` query to Flowmachine, which applies an iterative median filter to the output of another query. [#1339](https://github.com/Flowminder/FlowKit/issues/1339)
- FlowDB now includes the [TDS foreign data wrapper](https://github.com/tds-fdw). [#1729](https://github.com/Flowminder/FlowKit/issues/1729)
- Added contributing and support instructions. [#1791](https://github.com/Flowminder/FlowKit/issues/1791)
- New FlowETL module installable via pip to aid in ETL dag creation.

### Changed
- FlowDB is now built on PostgreSQL 12 [#1396](https://github.com/Flowminder/FlowKit/issues/1313) and PostGIS 3.
- FlowETL is now built on Airflow [10.1.6](https://airflow.apache.org/changelog.html#airflow-1-10-6-2019-10-28).
- FlowETL now defaults to disabling Airflow's REST API, and enables RBAC for the webui. [#1516](https://github.com/Flowminder/FlowKit/issues/1516)
- FlowETL now requires that the `FLOWETL_AIRFLOW_ADMIN_USERNAME` and `FLOWETL_AIRFLOW_ADMIN_PASSWORD` environment variables be set, which specify the default web ui account. [#1516](https://github.com/Flowminder/FlowKit/issues/1516)
- FlowAPI will no longer return a result for rows in spatial aggregate, joined spatial aggregate, flows, total events, meaningful locations aggregate, meaningful locations od, or unique subscriber count where the aggregate would contain less than 16 sims. [#1026](https://github.com/Flowminder/FlowKit/issues/1026)
- FlowETL now requires that `AIRFLOW__CORE__SQL_ALCHEMY_CONN` be provided as an environment variable or secret. [#1702](https://github.com/Flowminder/FlowKit/issues/1702), [#1703](https://github.com/Flowminder/FlowKit/issues/1703)
- FlowAuth now records last used two-factor authentication codes in an expiring cache, which supports either a file-based, or redis backend. [#1173](https://github.com/Flowminder/FlowKit/issues/1173)
- AutoFlow now uses [Bundler](https://bundler.io/) to manage Ruby dependencies.
- The `end_date` parameter of `flowclient.modal_location_from_dates` now refers to the day _after_ the final date included in the range, so is now consistent with other queries that have start/end date parameters. [#819](https://github.com/Flowminder/FlowKit/issues/819)
- Date intervals in AutoFlow date stencils are now interpreted as half-open intervals (i.e. including start date, excluding end date), for consistency with date ranges elsewhere in FlowKit.
- `flowmachine` user now has read access to ETL metadata tables in FlowDB

### Fixed
- Quickstart should no longer fail on systems which do not include the `netstat` tool. [#1472](https://github.com/Flowminder/FlowKit/issues/1472)
- Fixed an error that prevented FlowAuth admin users from resetting users' passwords using the FlowAuth UI. [#1635](https://github.com/Flowminder/FlowKit/issues/1635)
- The 'Cancel' button on the FlowAuth 'New User' form no longer submits the form. [#1636](https://github.com/Flowminder/FlowKit/issues/1636)
- FlowAuth backend now sends a meaningful 400 response when trying to create a user with an empty password. [#1637](https://github.com/Flowminder/FlowKit/issues/1637)
- Usernames of deleted users can now be re-used as usernames for new users. [#1638](https://github.com/Flowminder/FlowKit/issues/1638)
- RedactedJoinedSpatialAggregate now only redacts rows with too few subscribers. [#1747](https://github.com/Flowminder/FlowKit/issues/1747)
- FlowDB now uses a more conservative default setting for `tcp_keepalives_idle` of 10 minutes, to avoid connections being killed after 15 minutes when running in a docker swarm. [#1771](https://github.com/Flowminder/FlowKit/issues/1771)
- Aggregation units and api routes can now be added to servers. [#1815](https://github.com/Flowminder/FlowKit/issues/1815)
- Fixed several issues with FlowETL. [#1529](https://github.com/Flowminder/FlowKit/issues/1529) [#1499](https://github.com/Flowminder/FlowKit/issues/1499) [#1498](https://github.com/Flowminder/FlowKit/issues/1498) [#1497](https://github.com/Flowminder/FlowKit/issues/1497)

### Removed
- Removed pg_cron.


## [0.9.1]

### Added
- Added new `DistanceSeries` query to Flowmachine, which produces per-subscriber time series of distance from a reference point. [#1313](https://github.com/Flowminder/FlowKit/issues/1313)
- Added new `ImputedDistanceSeries` query to Flowmachine, which produces contiguous per-subscriber time series of distance from a reference point by filling in gaps using the rolling median. [#1337](https://github.com/Flowminder/FlowKit/issues/1337)

### Changed

### Fixed

- The FlowETL config file is now always validated, avoiding runtime errors if a config setting is wrong or missing. [#1375](https://github.com/Flowminder/FlowKit/issues/1375)
- FlowETL now only creates DAGs for CDR types which are present in the config, leading to a better user experience in the Airflow UI. [#1376](https://github.com/Flowminder/FlowKit/issues/1376)
- The `concurrency` settings in the FlowETL config are no longer ignored. [#1378](https://github.com/Flowminder/FlowKit/issues/1378)
- The FlowETL deployment example has been updated so that it no longer fails due to a missing foreign data wrapper for the available CDR dates. [#1379](https://github.com/Flowminder/FlowKit/issues/1379)
- Fixed error when editing a user in FlowAuth who did not have two factor enabled. [#1374](https://github.com/Flowminder/FlowKit/issues/1374)
- Fixed not being able to enable a newly added api route on existing servers in FlowAuth. [#1373](https://github.com/Flowminder/FlowKit/issues/1373)

### Removed

- The `default_args` section in the FlowETL config file has been removed. [#1377](https://github.com/Flowminder/FlowKit/issues/1377)


## [0.9.0]

### Added
- FlowAuth now makes version information available at `/version` and displays it in the web ui. [#835](https://github.com/Flowminder/FlowKit/issues/835)
- FlowETL now comes with a deployment example (in `flowetl/deployment_example/`). [#1126](https://github.com/Flowminder/FlowKit/issues/1126)
- FlowETL now allows to run supplementary post-ETL queries. [#989](https://github.com/Flowminder/FlowKit/issues/989)
- Random sampling is now exposed via the API, for all non-aggregated query kinds. [#1007](https://github.com/Flowminder/FlowKit/issues/1007)
- New aggregate added to FlowMachine - `HistogramAggregation`, which constructs histograms over the results of other queries. [#1075](https://github.com/Flowminder/FlowKit/issues/1075)
- New `IntereventInterval` query class - returns stats over the gap between events as a time interval.
- Added submodule `flowmachine.core.dependency_graph`, which contains functions related to creating or using query dependency graphs (previously these were in `utils.py`).
- New config option `sql_find_available_dates` in FlowETL to provide SQL code to determine the available dates. [#1295](https://github.com/Flowminder/FlowKit/issues/1295)

### Changed
- FlowDB is now based on PostgreSQL 11.5 and PostGIS 2.5.3
- When running queries through FlowAPI, the query's dependencies will also be cached by default. This behaviour can be switched off by setting `FLOWMACHINE_SERVER_DISABLE_DEPENDENCY_CACHING=true`. [#1152](https://github.com/Flowminder/FlowKit/issues/1152)
- `NewSubscribers` now takes a pair of `UniqueSubscribers` queries instead of the arguments to them
- Flowmachine's default random sampling method is now `random_ids` rather than the non-reproducible `system_rows`. [#1263](https://github.com/Flowminder/FlowKit/issues/1263)
- `IntereventPeriod` now returns stats over the gap between events in fractional time units, instead of time intervals. [#1265](https://github.com/Flowminder/FlowKit/issues/1265)
- Attempting to store a query that does not have a standard table name (e.g. `EventTableSubset` or unseeded random sample) will now raise an `UnstorableQueryError` instead of `ValueError`.
- In the FlowETL deployment example, the external ingestion database is now set up separately from the FlowKit components and connected to FlowDB via a docker overlay network. [#1276](https://github.com/Flowminder/FlowKit/issues/1276)
- The `md5` attribute of the `Query` class has been renamed to `query_id` [#1288](https://github.com/Flowminder/FlowKit/issues/1288).
- `DistanceMatrix` no longer returns duplicate rows for the lon-lat spatial unit.
- Previously, `Displacement` defaulted to returning `NaN` for subscribers who have a location in the reference location but were not seen in the time period for the displacement query. These subscribers are no longer returned unless the `return_subscribers_not_seen` argument is set to `True`.
- `PopulationWeightedOpportunities` is now available under `flowmachine.features.location`, instead of `flowmachine.models`
- `PopulationWeightedOpportunities` no longer supports erroring with incomplete per-location departure rate vectors and will instead omit any locations not included from the results
- `PopulationWeightedOpportunities` no longer requires use of the `run()` method

### Fixed
- Quickstart will no longer fail if it has been run previously with a different FlowDB data size and not explicitly shut down. [#900](https://github.com/Flowminder/FlowKit/issues/900)

### Removed
- Flowmachine's `subscriber_locations_cluster` function has been removed - use `HartiganCluster` or `MeaningfulLocations` directly.
- FlowAPI no longer supports the non-reproducible random sampling method `system_rows`. [#1263](https://github.com/Flowminder/FlowKit/issues/1263)


## [0.8.0]

### Added

- FlowAPI's 'joined_spatial_aggregate' endpoint now exposes event counts. [#992](https://github.com/Flowminder/FlowKit/issues/992)
- FlowAPI's 'joined_spatial_aggregate' endpoint now exposes top-up amount. [#967](https://github.com/Flowminder/FlowKit/issues/967)
- FlowAPI's 'joined_spatial_aggregate' endpoint now exposes nocturnal events. [#1025](https://github.com/Flowminder/FlowKit/issues/1025)
- FlowAPI's 'joined_spatial_aggregate' endpoint now exposes top-up balance. [#968](https://github.com/Flowminder/FlowKit/issues/968)
- FlowAPI's 'joined_spatial_aggregate' endpoint now exposes displacement. [#1010](https://github.com/Flowminder/FlowKit/issues/1010)
- FlowAPI's 'joined_spatial_aggregate' endpoint now exposes pareto interactions. [#1012](https://github.com/Flowminder/FlowKit/issues/1012)
- FlowETL now supports ingesting from a postgres table in addition to CSV files. [#1027](https://github.com/Flowminder/FlowKit/issues/1027)
- `FLOWETL_RUNTIME_CONFIG` environment variable added to control which DAG definitions the FlowETL integration tests should use (valid values: "testing", "production").
- `FLOWETL_INTEGRATION_TESTS_DISABLE_PULLING_DOCKER_IMAGES` environment variable added to allow running the FlowETL integration tests against locally built docker images during development.
- FlowAPI's 'joined_spatial_aggregate' endpoint now exposes handset. [#1011](https://github.com/Flowminder/FlowKit/issues/1011) and [#1029](https://github.com/Flowminder/FlowKit/issues/1029)
- `JoinedSpatialAggregate` now supports "distr" stats which computes outputs the relative distribution of the passed metrics.
- Added `SubscriberHandsetCharacteristic` to FlowMachine
- FlowAuth now supports optional two-factor authentication [#121](https://github.com/Flowminder/FlowKit/issues/121)

### Changed
- The flowdb containers for test_data and synthetic_data were split into two separate containers and quick_start.sh downloads the docker-compose files to a new temporary directory on each run. [#843](https://github.com/Flowminder/FlowKit/issues/843)
- Flowmachine now returns more informative error messages when query parameter validation fails. [#1055](https://github.com/Flowminder/FlowKit/issues/1055)


### Removed

- `TESTING` environment variable was removed (previously used by the FlowETL integration tests).
- Removed `SubscriberPhoneType` from FlowMachine to avoid redundancy.

## [0.7.0]

### Added

- `PRIVATE_JWT_SIGNING_KEY` environment variable/secret added to FlowAuth, which should be a PEM encoded RSA private key, optionally base64 encoded if supplied as an environment variable.
- `PUBLIC_JWT_SIGNING_KEY` environment variable/secret added to FlowAPI, which should be a PEM encoded RSA public key, optionally base64 encoded if supplied as an environment variable.
- The dev provisioning Ansible playbook now automatically generates an SSH key pair for the `flowkit` user. [#892](https://github.com/Flowminder/FlowKit/issues/892)
- Added new classes to represent spatial units in FlowMachine.
- Added a `Geography` query class, to get geography data for a spatial unit.
- FlowAPI's 'joined_spatial_aggregate' endpoint now exposes unique location counts.[#949](https://github.com/Flowminder/FlowKit/issues/949)
- FlowAPI's 'joined_spatial_aggregate' endpoint now exposes subscriber degree.[#969](https://github.com/Flowminder/FlowKit/issues/969)
- Flowdb now contains an auxiliary table to record outcomes of queries that can be run as part of the regular ETL process [#988](https://github.com/Flowminder/FlowKit/issues/988)

### Changed

- The quick-start script now only pulls the docker images for the services that are actually started up. [#898](https://github.com/Flowminder/FlowKit/issues/898)
- FlowAuth and FlowAPI are now linked using an RSA keypair, instead of per-server shared secrets. [#89](https://github.com/Flowminder/FlowKit/issues/89)
- Location-related FlowMachine queries now take a `spatial_unit` parameter instead of `level`.
- The quick-start script now uses the environment variable `GIT_REVISION` to control the version to be deployed.
- Create token page permission and spatial aggregation checkboxes are now hidden by default.[#834](https://github.com/Flowminder/FlowKit/issues/834)
- The flowetl mounted directories `archive, dump, ingest, quarantine` were replaced with a single `files` directory and files are no longer moved. [#946](https://github.com/Flowminder/FlowKit/issues/946)
- FlowDB's postgresql has been updated to [11.4](https://www.postgresql.org/about/news/1949/), which addresses several bugs and one major vulnerability.

### Fixed

- When creating a new token in FlowAuth, the expiry now always shows the year, seconds till expiry, and timezone. [#260](https://github.com/Flowminder/FlowKit/issues/260)
- Distances in `Displacement` are now calculated with longitude and latitude the corrcet way around. [#913](https://github.com/Flowminder/FlowKit/issues/913)
- The quick-start script now works correctly with branches. [#902](https://github.com/Flowminder/FlowKit/issues/902)
- Fixed `location_event_counts` failing to work when specifying a subset of event types [#1015](https://github.com/Flowminder/FlowKit/issues/1015)
- FlowAPI will now show the correct version in the API spec, flowmachine and flowclient will show the correct versions in the worked examples. [#818](https://github.com/Flowminder/FlowKit/issues/818)

### Removed
- Removed `cell_mappings.py`, `get_columns_for_level` and `BadLevelError`.

- `JWT_SECRET_KEY` has been removed in favour of RSA keys.
- The FlowDB tables `infrastructure.countries` and `infrastructure.operators` have been removed. [#958](https://github.com/Flowminder/FlowKit/issues/958)

## [0.6.4]

### Added

- Buttons to copy token to clipboard and download token as file added to token list page. [#704](https://github.com/Flowminder/FlowKit/issues/704)
- Two new worked examples: "Cell Towers Per Region" and "Unique Subscriber Counts". [#633](https://github.com/Flowminder/FlowKit/issues/633), [#634](https://github.com/Flowminder/FlowKit/issues/634)

### Changed

- The `FLOWDB_DEBUG` environment variable has been renamed to `FLOWDB_ENABLE_POSTGRES_DEBUG_MODE`.
- FlowAuth will now automatically set up the database when started without needing to trigger via the cli.
- FlowAuth now requires that at least one administrator account is created by providing env vars or secrets for:
  - `FLOWAUTH_ADMIN_PASSWORD`
  - `FLOWAUTH_ADMIN_USERNAME`

### Fixed

- The `FLOWDB_DEBUG` environment variable used to have no effect. This has been fixed. [#811](https://github.com/Flowminder/FlowKit/issues/811)
- Previously, queries could be stuck in an executing state if writing their cache metadata failed, they will now correctly show as having errored. [#833](https://github.com/Flowminder/FlowKit/issues/833)
- Fixed an issue where `Table` objects could be in an inconsistent cache state after resetting cache [#832](https://github.com/Flowminder/FlowKit/issues/832)
- FlowAuth's docker container can now be used with a Postgres backing database. [#825](https://github.com/Flowminder/FlowKit/issues/825)
- FlowAPI now starts up successfully when following the "Secrets Quickstart" instructions in the docs. [#836](https://github.com/Flowminder/FlowKit/issues/836)
- The command to generate an SSL certificate in the "Secrets Quickstart" section in the docs has been fixed and made more robust [#837](https://github.com/Flowminder/FlowKit/issues/837)
- FlowAuth will no longer try to initialise the database or create demo data multiple times when running under uwsgi with multiple workers [#844](https://github.com/Flowminder/FlowKit/issues/844)
- Fixed issue of Multiple tokens don't line up on FlowAuth "Tokens" page [#849](https://github.com/Flowminder/FlowKit/issues/849)

### Removed

- The `FLOWDB_SERVICES` environment variable has been removed from the toplevel Makefile, so that now `DOCKER_SERVICES` is the only environment variable that controls which services are spun up when running `make up`. [#827](https://github.com/Flowminder/FlowKit/issues/827)

## [0.6.3]

### Added

- FlowKit's worked examples are now Dockerized, and available as part of the quick setup script [#614](https://github.com/Flowminder/FlowKit/issues/614)
- Skeleton for Airflow based ETL system added with basic ETL DAG specification and tests.
- The docs now contain information about required versions of installation prerequisites [#703](https://github.com/Flowminder/FlowKit/issues/703)
- FlowAPI now requires the `FLOWAPI_IDENTIFIER` environment variable to be set, which contains the name used to identify this FlowAPI server when generating tokens in FlowAuth [#727](https://github.com/Flowminder/FlowKit/issues/727)
- `flowmachine.utils.calculate_dependency_graph` now includes the `Query` objects in the `query_object` field of the graph's nodes dictionary [#767](https://github.com/Flowminder/FlowKit/issues/767)
- Architectural Decision Records (ADR) have been added and are included in the auto-generated docs [#780](https://github.com/Flowminder/FlowKit/issues/780)
- Added FlowDB environment variables `SHARED_BUFFERS_SIZE` and `EFFECTIVE_CACHE_SIZE`, to allow manually setting the Postgres configuration parameters `shared_buffers` and `effective_cache_size`.
- The function `print_dependency_tree()` now takes an optional argument `show_stored` to display information whether dependent queries have been stored or not [#804](https://github.com/Flowminder/FlowKit/issues/804)
- A new function `plot_dependency_graph()` has been added which allows to conveniently plot and visualise a dependency graph for use in Jupyter notebooks (this requires IPython and pygraphviz to be installed) [#786](https://github.com/Flowminder/FlowKit/issues/786)

### Changed

- Parameter names in `flowmachine.connect()` have been renamed as follows to be consistent with the associated environment variables [#728](https://github.com/Flowminder/FlowKit/issues/728):
  - `db_port -> flowdb_port`
  - `db_user -> flowdb_user`
  - `db_pass -> flowdb_password`
  - `db_host -> flowdb_host`
  - `db_connection_pool_size -> flowdb_connection_pool_size`
  - `db_connection_pool_overflow -> flowdb_connection_pool_overflow`
- FlowAPI and FlowAuth now expect an audience key to be present in tokens [#727](https://github.com/Flowminder/FlowKit/issues/727)
- Dependent queries are now only included once in the md5 calculation of a given query (in particular, it changes the query ids compared to previous FlowKit versions).
- Error is displayed in the add user form of Flowauth if username is alredy exists. [#690](https://github.com/Flowminder/FlowKit/issues/690)
- Error is displayed in the add group form of Flowauth if group name already exists. [#709](https://github.com/Flowminder/FlowKit/issues/709)
- FlowAuth's add new server page now shows helper text for bad inputs. [#749](https://github.com/Flowminder/FlowKit/pull/749)
- The class `SubscriberSubsetterBase` in FlowMachine no longer inherits from `Query` [#740](https://github.com/Flowminder/FlowKit/issues/740) (this changes the query ids compared to previous FlowKit versions).

### Fixed

- FlowClient docs rendered to website now show the options available for arguments that require a string from some set of possibilities [#695](https://github.com/Flowminder/FlowKit/issues/695).
- The Flowmachine loggers are now initialised only once when flowmachine is imported, with a call to `connect()` only changing the log level [#691](https://github.com/Flowminder/FlowKit/issues/691)
- The FERNET_KEY environment variable for FlowAuth is now named FLOWAUTH_FERNET_KEY
- The quick-start script now correctly aborts if one of the FlowKit services doesn't fully start up [#745](https://github.com/Flowminder/flowkit/issues/745)
- The maps in the worked examples docs pages now appear in any browser
- Example invocations of `generate-jwt` are no longer uncopyable due to line wrapping [#778](https://github.com/Flowminder/flowkit/issues/745)
- API parameter `interval` for `location_event_counts` queries is now correctly passed to the underlying FlowMachine query object [#807](https://github.com/Flowminder/FlowKit/issues/807).

## [0.6.2]

### Added

- Added a new module, `flowkit-jwt-generator`, which generates test JWT tokens for use with FlowAPI [#564](https://github.com/Flowminder/FlowKit/issues/564)
- A new Ansible playbook was added in `deployment/provision-dev.yml`. In addition to the standard provisioning
  this installs pyenv, Python 3.7, pipenv and clones the FlowKit repository, which is useful for development purposes.
- Added a 'quick start' setup script for trying out a complete FlowKit system [#688](https://github.com/Flowminder/FlowKit/issues/688).

### Changed

- FlowAPI's `available_dates` endpoint now always returns available dates for all event types and does not accept JSON
- Hints are now displayed in the add user form of FlowAuth if the form is not completed [#679](https://github.com/Flowminder/FlowKit/issues/679)
- Error messages are now displayed when generating a new token in FlowAuth if the token's name is invalid [#799](https://github.com/Flowminder/FlowKit/issues/799)
- The Ansible playbooks in `deployment/` now allow configuring the username and password for the FlowKit user account.
- Default compose file no longer includes build blocks, these have been moved to `docker-compose-build.yml`.

### Fixed

- FlowDB synthetic data container no longer silently fails to generate data if data generator is not set [#654](https://github.com/Flowminder/FlowKit/issues/654)

## [0.6.1]

### Fixed

- Fixed `TotalNetworkObjects` raising an error when run with a lat-long level [#108](https://github.com/Flowminder/FlowKit/issues/108)
- Radius of gyration no longer incorrectly appears as a top level api query

## [0.6.0]

### Added

- Added new flowclient API entrypoint, `aggregate_network_objects`, to access equivalent flowmachine query [#601](https://github.com/Flowminder/FlowKit/issues/601)
- FlowAPI now exposes the API spec at the `spec/openapi.json` endpoint, and an interactive version of the spec at the `spec/redoc` endpoint
- Added Makefile target `make up-no_build`, to spin up all containers without building the images
- Added `resync_redis_with_cache` function to cache utils, to allow administrators to align redis with FlowDB [#636](https://github.com/Flowminder/FlowKit/issues/636)
- Added new flowclient API entrypoint, `radius_of_gyration`, to access (with simplified parameters) equivalent flowmachine query `RadiusOfGyration` [#602](https://github.com/Flowminder/FlowKit/issues/602)

### Changed

- The `period` argument to `TotalNetworkObjects` in FlowMachine has been renamed `total_by`
- The `period` argument to `total_network_objects` in FlowClient has been renamed `total_by`
- The `by` argument to `AggregateNetworkObjects` in FlowMachine has been renamed to `aggregate_by`
- The `stop_date` argument to the `modal_location_from_dates` and `meaningful_locations_*` functions in FlowClient has been renamed `end_date` [#470](https://github.com/Flowminder/FlowKit/issues/470)
- `get_result_by_query_id` now accepts a `poll_interval` argument, which allows polling frequency to be changed
- The `start` and `stop` argument to `EventTableSubset` are now mandatory.
- `RadiusOfGyration` now returns a `value` column instead of an `rog` column
- `TotalNetworkObjects` and `AggregateNetworkObjects` now return a `value` column, rather than `statistic_name`
- All environment variables are now in a single `development_environment` file in the project root, development environment setup has been simplified
- Default FlowDB users for FlowMachine and FlowAPI have changed from "analyst" and "reporter" to "flowmachine" and "flowapi", respectively
- Docs and integration tests now use top level compose file
- The following environment variables have been renamed:
  - `FLOWMACHINE_SERVER` (FlowAPI) -> `FLOWMACHINE_HOST`
  - `FM_PASSWORD` (FlowDB), `FLOWDB_PASS` (FlowMachine) -> `FLOWMACHINE_FLOWDB_PASSWORD`
  - `API_PASSWORD` (FlowDB), `FLOWDB_PASS` (FlowAPI) -> `FLOWAPI_FLOWDB_PASSWORD`
  - `FM_USER` (FlowDB), `FLOWDB_USER` (FlowMachine) -> `FLOWMACHINE_FLOWDB_USER`
  - `API_USER` (FlowDB), `FLOWDB_USER` (FlowAPI) -> `FLOWAPI_FLOWDB_USER`
  - `LOG_LEVEL` (FlowMachine) -> `FLOWMACHINE_LOG_LEVEL`
  - `LOG_LEVEL` (FlowAPI) -> `FLOWAPI_LOG_LEVEL`
  - `DEBUG` (FlowDB) -> `FLOWDB_DEBUG`
  - `DEBUG` (FlowMachine) -> `FLOWMACHINE_SERVER_DEBUG_MODE`
- The following Docker secrets have been renamed:
  - `FLOWAPI_DB_USER` -> `FLOWAPI_FLOWDB_USER`
  - `FLOWAPI_DB_PASS` -> `FLOWAPI_FLOWDB_PASSWORD`
  - `FLOWMACHINE_DB_USER` -> `FLOWMACHINE_FLOWDB_USER`
  - `FLOWMACHINE_DB_PASS` -> `FLOWMACHINE_FLOWDB_PASSWORD`
  - `POSTGRES_PASSWORD_FILE` -> `POSTGRES_PASSWORD`
  - `REDIS_PASSWORD_FILE` -> `REDIS_PASSWORD`
- `status` enum in FlowDB renamed to `etl_status`
- `reset_cache` now requires a redis client argument

### Fixed

- Fixed being unable to add new users or servers when running FlowAuth with a Postgres database [#622](https://github.com/Flowminder/FlowKit/issues/622)
- Resetting the cache using `reset_cache` will now reset the state of queries in redis as well [#650](https://github.com/Flowminder/FlowKit/issues/650)
- Fixed `mode` statistic for `AggregateNetworkObjects` [#651](https://github.com/Flowminder/FlowKit/issues/651)

### Removed

- Removed `docker-compose-dev.yml`, and docker-compose files in `docs/`, `flowdb/tests/` and `integration_tests/`.
- Removed `Dockerfile-dev` Dockerfiles
- Removed `ENV` defaults from the FlowMachine Dockerfile
- Removed `POSTGRES_DB` environment variable from FlowDB Dockerfile, database name is now hardcoded as `flowdb`

## [0.5.3]

### Added

- Added new `spatial_aggregate` API endpoint and FlowClient function [#599](https://github.com/Flowminder/FlowKit/issues/599)
- Added new flowclient API entrypoint, total_network_objects(), to access (with simplified parameters) equivalent flowmachine query [#581](https://github.com/Flowminder/FlowKit/issues/581)
- Added new flowclient API entrypoint, location_introversion(), to access (with simplified parameters) equivalent flowmachine query [#577](https://github.com/Flowminder/FlowKit/issues/577)
- Added new flowclient API entrypoint, unique_subscriber_counts(), to access (with simplified parameters) equivalent flowmachine query [#562](https://github.com/Flowminder/FlowKit/issues/562)
- New schema `aggregates` and table `aggregates.aggregates` have been created for maintaining a record of the process and completion of scheduled aggregates.
- New `joined_spatial_aggregate` API endpoint and FlowClient function [#600](https://github.com/Flowminder/FlowKit/issues/600)

### Changed

- `daily_location` and `modal_location` query types are no longer accepted as top-level queries, and must be wrapped using `spatial_aggregate`
- `JoinedSpatialAggregate` no longer accepts positional arguments
- `JoinedSpatialAggregate` now supports "avg", "max", "min", "median", "mode", "stddev" and "variance" stats

### Fixed

- `total_network_objects` no longer returns results from `AggregateNetworkObjects` [#603](https://github.com/Flowminder/FlowKit/issues/603)

## [0.5.2]

### Fixed

- Fixed [#514](https://github.com/Flowminder/FlowKit/issues/514), which would cause the client to hang after submitting a query that couldn't be created
- Fixed [#575](https://github.com/Flowminder/FlowKit/issues/575), so that events at midnight are now considered to be happening on the following day

## [0.5.1]

### Added

- Added `HandsetStats` to FlowMachine.
- Added new `ContactReferenceLocationStats` query class to FlowMachine.
- A new zmq message `get_available_dates` was added to the flowmachine server, along with the `/available_dates`
  endpoint in flowapi and the function `get_available_dates()` in flowclient. These allow to determine the dates
  that are available in the database for the supported event types.

### Changed

- FlowMachine's debugging logs are now from a single logger (`flowmachine.debug`) and include the submodule in the submodule field instead of using it as the logger name
- FlowMachine's query run logger now uses the logger name `flowmachine.query_run_log`
- FlowAPI's access, run and debug loggers are now named `flowapi.access`, `flowapi.query` and `flowapi.debug`
- FlowAPI's access and run loggers, and FlowMachine's query run logger now log to stdout instead of stderr
- Passwords for Redis and FlowDB must now be explicitly provided to flowmachine via argument to `connect`, env var, or secret

### Removed

- FlowMachine and FlowAPI no longer support logging to a file

## [0.5.0]

### Added

- The flowmachine python library is now pip installable (`pip install flowmachine`)
- The flowmachine server now supports additional actions: `get_available_queries`, `get_query_schemas`, `ping`.
- Flowdb now contains a new `dfs` schema and associated tables to process mobile money transactions.
  In addition, `flowdb_testdata` contains sample data for DFS transactions.
- The docs now include three worked examples of CDR analysis using FlowKit.
- Flowmachine now supports calculating the total amount of various DFS metrics (transaction amount,
  commission, fee, discount) per aggregation unit during a given date range. These metrics are also
  exposed in FlowAPI via the query kind `dfs_metric_total_amount`.

### Changed

- The JSON structure when setting queries running via flowapi or the flowmachine server has changed:
  query parameters are now "inlined" alongside the `query_kind` key, rather than nested using a separate `params` key.
  Example:
  - previously: `{"query_kind": "daily_location", "params": {"date": "2016-01-01", "aggregation_unit": "admin3", "method": "last"}}`,
  - now: `{"query_kind": "daily_location", "date": "2016-01-01", "aggregation_unit": "admin3", "method": "last"}`
- The JSON structure of zmq reply messages from the flowmachine server was changed.
  Replies now have the form: `{"status": "[success|error]", "msg": "...", "payload": {...}`.
- The flowmachine server action `get_sql` was renamed to `get_sql_for_query_result`.
- The parameter `daily_location_method` was renamed to `method`.

## [0.4.3]

### Added

- When running integration tests locally, normally pytest will automatically spin up servers for flowmachine and flowapi as part of the test setup.
  This can now be disabled by setting the environment variable `FLOWKIT_INTEGRATION_TESTS_DISABLE_AUTOSTART_SERVERS=TRUE`.
- The integration tests now use the environment variables `FLOWAPI_HOST`, `FLOWAPI_PORT` to determine how to connect to the flowapi server.
- A new data generator has been added to the synthetic data container which supports more data types, simple disaster simulation, and more plausible behaviours as well as increased performance

### Changed

- FlowAPI now reports queued/running status for queries instead of just accepted
- The following environment variables have been renamed:
  - `DB_USER` -> `FLOWDB_USER`
  - `DB_USER` -> `FLOWDB_HOST`
  - `DB_PASS` -> `FLOWDB_PASS`
  - `DB_PW` -> `FLOWDB_PASS`
  - `API_DB_USER` -> `FLOWAPI_DB_USER`
  - `API_DB_PASS` -> `FLOWAPI_DB_PASS`
  - `FM_DB_USER` -> `FLOWMACHINE_DB_USER`
  - `FM_DB_PASS` -> `FLOWMACHINE_DB_PASS`
- Added `numerator_direction` to `ProportionEventType` to allow for proportion of directed events.

### Fixed

- Server no longer loses track of queries under heavy load
- `TopUpBalances` no longer always uses entire topups table

### Removed

- The environment variable `DB_NAME` has been removed.

## [0.4.2]

### Changed

- `MDSVolume` no longer allows specifying the table, and will always use the `mds` table.
- All FlowMachine logs are now in structured json form
- FlowAPI now uses structured logs for debugging messages

## [0.4.1]

### Added

- Added `TopUpAmount`, `TopUpBalance` query classes to FlowMachine.
- Added `PerLocationEventStats`, `PerContactEventStats` to FlowMachine

### Removed

- Removed `TotalSubscriberEvents` from FlowMachine as it is superseded by `EventCount`.

## [0.4.0]

### Added

- Dockerised development setup, with support for live reload of `flowmachine` and `flowapi` after source code changes.
- Pre-commit hook for Python formatting with black.
- Added new `IntereventPeriod`, `ContactReciprocal`, `ProportionContactReciprocal`, `ProportionEventReciprocal`, `ProportionEventType` and `MDSVolume` query classes to FlowMachine.

### Changed

- `CustomQuery` now requires column names to be specified
- Query classes are now required to declare the column names they return via the `column_names` property
- FlowAPI now reports whether a query is queued or running when polling
- FlowDB test data and synthetic data images are now available from their own Docker repos (Flowminder/flowdb-testdata, Flowminder/flowdb-synthetic-data)
- Changed query class name from `NocturnalCalls` to `NocturnalEvents`.

### Fixed

- FlowAPI is now an installable python module

### Removed

- Query objects can no longer be recalculated to cache and must be explicitly removed first
- Arbitrary `Flow` maths
- `EdgeList` query type
- Removes query class `ProportionOutgoing` as it becomes redundant with the the introduction of `ProportionEventType`.

## [0.3.0]

### Added

- API route for retrieving geography data from FlowDB
- Aggregated meaningful locations are now available via FlowAPI
- Origin-destination matrices between meaningful locations are now available via FlowAPI
- Added new `MeaningfulLocations`, `MeaningfulLocationsAggregate` and `MeaningfulLocationsOD` query classes to FlowMachine

### Changed

- Constructors for `HartiganCluster`, `LabelEventScore`, `EventScore` and `CallDays` now have different signatures
- Restructured and extended documentation; added high-level overview and more targeted information for different types of users

## [0.2.2]

### Added

- Support for running FlowDB as an arbitrary user via docker's `--user` flag

### Removed

- Support for setting the uid and gid of the postgres user when building FlowDB

## [0.2.1]

### Fixed

- Fixed being unable to build if the port used by `git://` is not open

## [0.2.0]

### Added

- Added utilities for managing and inspecting the query cache

## [0.1.2]

### Changed

- FlowDB now requires a password to be set for the flowdb superuser

## [0.1.1]

### Added

- Support for password protected redis

### Changed

- Changed the default redis image to bitnami's redis (to enable password protection)

## [0.1.0]

### Added

- Added structured logging of access attempts, query running, and data access
- Added CHANGELOG.md
- Added support for Postgres JIT in FlowDB
- Added total location events metric to FlowAPI and FlowClient
- Added ETL bookkeeping schema to FlowDB

### Changed

- Added changelog update to PR template
- Increased default shared memory size for FlowDB containers

### Fixed

- Fixed being unable to delete groups in FlowAuth
- Fixed `make up` not working with defaults

## [0.0.5]

### Added

- Added Python 3.6 support for FlowClient

[unreleased]: https://github.com/Flowminder/FlowKit/compare/1.1.1...master
[1.1.1]: https://github.com/Flowminder/FlowKit/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/Flowminder/FlowKit/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/Flowminder/FlowKit/compare/0.9.1...1.0.0
[0.9.1]: https://github.com/Flowminder/FlowKit/compare/0.9.0...0.9.1
[0.9.0]: https://github.com/Flowminder/FlowKit/compare/0.8.0...0.9.0
[0.8.0]: https://github.com/Flowminder/FlowKit/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/Flowminder/FlowKit/compare/0.6.4...0.7.0
[0.6.4]: https://github.com/Flowminder/FlowKit/compare/0.6.3...0.6.4
[0.6.3]: https://github.com/Flowminder/FlowKit/compare/0.6.2...0.6.3
[0.6.2]: https://github.com/Flowminder/FlowKit/compare/0.6.1...0.6.2
[0.6.1]: https://github.com/Flowminder/FlowKit/compare/0.6.0...0.6.1
[0.6.0]: https://github.com/Flowminder/FlowKit/compare/0.5.3...0.6.0
[0.5.3]: https://github.com/Flowminder/FlowKit/compare/0.5.2...0.5.3
[0.5.2]: https://github.com/Flowminder/FlowKit/compare/0.5.1...0.5.2
[0.5.1]: https://github.com/Flowminder/FlowKit/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/Flowminder/FlowKit/compare/0.4.3...0.5.0
[0.4.3]: https://github.com/Flowminder/FlowKit/compare/0.4.2...0.4.3
[0.4.2]: https://github.com/Flowminder/FlowKit/compare/0.4.1...0.4.2
[0.4.1]: https://github.com/Flowminder/FlowKit/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/Flowminder/FlowKit/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/Flowminder/FlowKit/compare/0.2.2...0.3.0
[0.2.2]: https://github.com/Flowminder/FlowKit/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/Flowminder/FlowKit/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/Flowminder/FlowKit/compare/0.1.2...0.2.0
[0.1.2]: https://github.com/Flowminder/FlowKit/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/Flowminder/FlowKit/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/Flowminder/FlowKit/compare/0.0.5...0.1.0
[0.0.5]: https://github.com/Flowminder/FlowKit/compare/0.0.4...0.0.5
