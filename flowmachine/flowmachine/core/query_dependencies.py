# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class ContributesToQueryDependencyGraph:
    """
    This is a mixin class which helps to keep track
    of dependencies between query objects (and other
    contributing classes).

    If a class inherits from this mixin, this marks it
    as being taken into consideration when constructing
    the dependency graph for a query object.

    This is automatically the case for classes inheriting
    from Query, but it can also be used by other classes
    which do not represent full query objects but contribute
    to their construction (for example subsetters).
    """
