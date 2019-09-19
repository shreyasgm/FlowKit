# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# -*- coding: utf-8 -*-
"""
The population-weighted opportunities model uses
population distributions for predicting the
probability of movement between populated
areas. The model computes the attraction
between populated centers relative to the
distance between each origin and destination
locations and also to all other equidistant
locations from the destination. The model
works similarly to the Radiation Model.

The original publication suggests that its
ideal usage is in cities.



References
----------
    Yan X-Y, Zhao C, Fan Y, Di Z, Wang W-X. 2014 "Universal predictability of mobility patterns in cities". J. R. Soc. Interface 11: 20140834. http://dx.doi.org/10.1098/rsif.2014.0834

"""

import warnings
from typing import List, Optional

import pandas as pd

from flowmachine.features import daily_location
from flowmachine.utils import list_of_dates
from ..features import ModalLocation
from ..core.query import Query
from ..core.model import Model, model_result
from ..core import make_spatial_unit
from ..core.spatial_unit import LonLatSpatialUnit
from ..features.spatial.distance_matrix import DistanceMatrix

import structlog

logger = structlog.get_logger("flowmachine.debug", submodule=__name__)


class _populationBuffer(Query):
    """
    Private class for calculating a population
    vector based on buffers generated from
    the distance radii between point locations.

    Parameters
    ----------
    population_object : flowmachine.features.utilities.spatial_aggregates.SpatialAggregate
        An aggregated subscriber locating object
    distance_matrix : flowmachine.features.spatial.distance_matrix.DistanceMatrix
        A distance matrix
    """

    def __init__(self, population_object, distance_matrix):
        self.population_object = population_object
        self.distance_matrix = distance_matrix
        self.spatial_unit = self.distance_matrix.spatial_unit

        super().__init__()

    def __get_location_buffer(self):
        """
        Protected method for generating SQL
        for the buffer areas between a location
        (i..e an origin) and all its possible
        counterparts (i.e. destinations).
        """
        cols = self.spatial_unit.location_id_columns

        from_cols = ", ".join(f"{c}_from" for c in cols)
        to_cols = ", ".join(f"{c}_to" for c in cols)
        sql = f"""

            SELECT
                {from_cols},
                {to_cols},
                A.value AS distance,
                A.geom_origin AS geom_origin,
                A.geom_destination AS geom_destination,
                ST_Buffer(A.geom_destination::geography, A.value * 1000) AS geom_buffer
            FROM ({self.distance_matrix.geom_matrix.get_query()}) AS A

        """

        return sql

    @property
    def column_names(self) -> List[str]:
        cols = self.spatial_unit.location_id_columns

        return (
            ["id"]
            + [f"{c}_from" for c in cols]
            + [f"{c}_to" for c in cols]
            + ["distance", "buffer_population", "n_sites"]
        )

    def _make_query(self):
        """
        Protected method that generates SQL
        that calculates the population that is
        covered by a buffer.
        """
        cols = self.spatial_unit.location_id_columns

        sql = f"""
        WITH foo as (SELECT * FROM 
        (SELECT {", ".join(f"hl_{direction}.{c} as {c}_{direction}" for c in cols for direction in ("to", "from"))}, hl_from.total as src_pop, hl_to.total as sink_pop
        FROM
        ({self.population_object.get_query()}) as hl_from
        CROSS JOIN 
        ({self.population_object.get_query()}) as hl_to
        ) pops
        LEFT JOIN
        ({self.distance_matrix.get_query()}) as dm
        USING ({", ".join(f"{c}_{direction}" for c in cols for direction in ("to", "from") if c != "value")}))
        select row_number() OVER(ORDER BY value) as id,  
        {", ".join(f"{c}_{direction}" for direction in ("from", "to") for c in cols  if c != "value")},
         value*1000 as distance, 
         sum(src_pop) over (partition by {", ".join(f"{c}_to" for c in cols if c != "value")} order by value)-src_pop as buffer_population, 
         row_number() over (partition by {", ".join(f"{c}_to" for c in cols if c != "value")} order by value) as n_sites 
         from foo 
        
        """

        return sql


class PopulationWeightedOpportunities(Model):
    """
    Population-weighted opportunities model [1]_.



    The model predicts the mobility between populated
    areas in cities based only on the population densities
    of those areas, their spatial distribution, and
    the number of people that depart a certain area. This
    model is useful for studying mobility pattern in cities.

    Parameters
    ----------
    start : str
        Start of time period to analyse.

    stop : str
        Stop of time period to analyse.

    method : str
        Method used to calculate population using the
        Population() recipe. 'home-location' is the
        default method used. Refer to the Population()
        documentation for other available methods.

    spatial_unit : flowmachine.core.spatial_unit.*SpatialUnit, default versioned-site
        Note: DistanceMatrix only supports spatial units with 'lon' and 'lat'
        columns at this time.

    **kwargs : arguments
        Used to pass custom arguments to the ModalLocation() objects.

    Examples
    --------
    Much like other `flowmachine` classes, this model
    has to be instantiated:

    >>> p = PopulationWeightedOpportunities('2016-01-01', '2016-01-07')

    After instantiation, the model will run using the
    PopulationWeightedOpportunities().run() method
    as follows:

    >>> p.run(departure_rate_vector={'0xqNDj': 0.9}, ignore_missing=True)

    One can also run the model with uniform departure
    rates for all locations as follows:

    >>> p.run(uniform_departure_rate=0.5)
        origin  destination  prediction  probability
    0  0xqNDj        8wPojr    0.384117     0.010670
    1  0xqNDj        B8OaG5    0.344384     0.009566
    2  0xqNDj        DonxkP    0.715311     0.019870
    3  0xqNDj        zdNQx2    0.267854     0.007440

    Where prediction is the absolute number of people
    that move from one location to another. (This should
    be interpreted as a integer, but floats are provided
    for evaluating results in a continuous scale.) And
    probability is the predicted value over the total
    population leaving the origin (T_i). That is, how
    likely it is that a person leaving the origin will
    be found in a given destination.

    References
    ----------
    .. [1] Yan X-Y, Zhao C, Fan Y, Di Z, Wang W-X. 2014 "Universal predictability of mobility patterns in cities". J. R. Soc. Interface 11: 20140834. http://dx.doi.org/10.1098/rsif.2014.0834

    """

    def __init__(
        self,
        start,
        stop,
        method="home-location",
        spatial_unit: Optional[LonLatSpatialUnit] = None,
        **kwargs,
    ):

        warnings.warn(
            "The PWO model is currently **experimental**. "
            + "Please review Yan X-Y et al. "
            + "(http://dx.doi.org/10.1098/rsif.2014.0834) "
            + "before using this model in production."
        )

        self.start = start
        self.stop = stop
        self.method = method
        if spatial_unit is None:
            self.spatial_unit = make_spatial_unit("versioned-site")
        else:
            self.spatial_unit = spatial_unit
        self.distance_matrix = DistanceMatrix(
            spatial_unit=self.spatial_unit, return_geometry=True
        )

        if self.method == "home-location":
            self.population_object = ModalLocation(
                *[
                    daily_location(d, spatial_unit=self.spatial_unit, **kwargs)
                    for d in list_of_dates(self.start, self.stop)
                ]
            ).aggregate()

        self.population_buffer_object = _populationBuffer(
            population_object=self.population_object,
            distance_matrix=self.distance_matrix,
        )

    def __get_population(self, df, i):
        """
        Protected getter method for getting
        the location value of the self.population_df
        DataFrame.

        Parameters
        ----------
        i : object
            The index in the self.population_df DataFrame
            containing the location identifier.

        Returns
        -------
        A float value with the population value
        for location i.

        """
        return df.loc[tuple(i), "total"]

    def __get_buffer_population(self, df, i, j):
        """
        Protected getter method for getting
        the location value of the self.population_buffer
        DataFrame.

        Parameters
        ----------
        i : str
            Location identifier of the origin location
            in the self.population_buffer DataFrame.
        j : str
            Location identifier of the destination location
            in the self.population_buffer DataFrame.

        Returns
        -------
        A float value with the population value for
        a pair of origin (i) and destination (j)
        locations.

        """
        filtered = df.loc[tuple(i + j)]

        return filtered["buffer_population"]

    @model_result
    def run(
        self,
        uniform_departure_rate=0.1,
        departure_rate_vector=None,
        ignore_missing=False,
    ):
        """
        Runs model.

        Parameters
        ----------
        uniform_departure_rate : float
            Proportion of population from location i
            that will be departing in observed time period.
            This proportion applies to all locations
            uniformly.

        departure_rate_vector : dict
            A dictionary that contains the proportion
            of the population from locations i that have
            departed those locations. The keys of the
            dictionaries must be the location identifier
            and the values the departure rate.
            If passed, this will be used over the
            `uniform_departure_rate` parameter.

        ignore_missing : bool
            If True, existing locations that are not
            found in the departure_rate_vector dictionary
            will be computed using zero departures.

        Returns
        -------
        A pandas dataframe with a mobility matrix.

        """

        if "population_buffer" not in self.__dict__.keys():
            logger.warning(
                " Computing Population() and DistanceMatrix() "
                + "objects. This can take a few minutes."
            )

            population_df = self.population_object.get_dataframe()
            population_buffer = self.population_buffer_object.get_dataframe()
            ix = [
                "{}_{}".format(c, d)
                for d in ("from", "to")
                for c in self.spatial_unit.location_id_columns
            ]
            population_buffer.set_index(ix, inplace=True)

            M = population_df["total"].sum()
            N = len(
                population_df[self.spatial_unit.location_id_columns].drop_duplicates()
            )
            beta = 1 / M

            locations = population_df[
                self.spatial_unit.location_id_columns
            ].values.tolist()
            population_df.set_index(self.spatial_unit.location_id_columns, inplace=True)

        if not departure_rate_vector:
            logger.warning(
                " Using an uniform departure "
                + "rate of {} for ".format(uniform_departure_rate)
                + "all locations."
            )
        elif not ignore_missing and len(departure_rate_vector) != len(locations):
            raise ValueError(
                "Locations missing from "
                + "`departure_rate_vector`. Use "
                + "ignore_missing=True if locations "
                + "without rates should be ignored."
            )

        results = []
        for i in locations:
            sigma = 0
            m_i = self.__get_population(population_df, i)

            if departure_rate_vector:
                try:
                    T_i = m_i * departure_rate_vector[i[0]]
                except KeyError:
                    try:
                        T_i = m_i * departure_rate_vector[tuple(i[:1])]
                    except KeyError:
                        T_i = 0
            else:
                T_i = m_i * uniform_departure_rate

            for k in [l for l in locations if l != i]:
                m_k = self.__get_population(population_df, k)
                S_ik = self.__get_buffer_population(population_buffer, i, k)

                sigma += m_k * ((1 / S_ik) - beta)

            for j in [l for l in locations if l != i]:
                m_j = self.__get_population(population_df, j)
                S_ij = self.__get_buffer_population(population_buffer, i, j)

                T_ij = (T_i * m_j * ((1 / S_ij) - beta)) / sigma

                if T_i != 0:
                    probability = T_ij / T_i
                else:
                    probability = 0

                results.append(i + j + [T_ij, probability])
        ix = [
            "{}_{}".format(c, d)
            for d in ("from", "to")
            for c in self.spatial_unit.location_id_columns
        ]
        ix += ["prediction", "probability"]
        res = pd.DataFrame(results, columns=ix)
        return res
