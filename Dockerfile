# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Worked examples docker container
# Provides all worked examples from the FlowKit docs in a ready-to-go JupyterLab install
#

FROM jupyter/scipy-notebook:latest@sha256:dc2b7aac066f101107128d825d51b56cb1abd5bcbbc2b5f2ec0a03c3114f75e6

RUN rm -rf /home/$NB_USER/work
ARG SOURCE_VERSION=0+unknown
ENV SOURCE_VERSION=${SOURCE_VERSION}
ENV SOURCE_TREE=FlowKit-${SOURCE_VERSION}
COPY docs/source/worked_examples/*.ipynb /home/$NB_USER/
COPY flowmachine /${SOURCE_TREE}/flowmachine
COPY flowclient /${SOURCE_TREE}/flowclient
USER root
RUN cd /${SOURCE_TREE}/flowclient && python setup.py bdist_wheel && \
    cd /${SOURCE_TREE}/flowmachine && python setup.py bdist_wheel && \
    fix-permissions /${SOURCE_TREE}
USER $NB_UID
RUN pip install geopandas mapboxgl /${SOURCE_TREE}/flowclient/dist/*.whl \
     /${SOURCE_TREE}/flowmachine/dist/*.whl && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER && \
    cd /home/$NB_USER/ && jupyter trust -y *
