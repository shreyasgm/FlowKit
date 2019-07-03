# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# -*- coding: utf-8 -*-
"""
Tests for configuration parsing
"""
import pytest
import yaml

from copy import deepcopy
from pathlib import Path
from pendulum import parse

from etl.config_parser import validate_config, get_config_from_file
from etl.etl_utils import CDRType, find_files, parse_file_name


def test_config_validation(sample_config_dict):
    """
    Check that with valid config dict we get no exception
    """
    validate_config(global_config_dict=sample_config_dict)


def test_config_validation_fails_no_etl_section(sample_config_dict):
    """
    Check that we get an exception raised if etl subsection
    missing. The exception will also contain two other exceptions.
    One for missing etl section and one for missing etl subsections.
    """
    bad_config = deepcopy(sample_config_dict)
    bad_config.pop("etl")

    with pytest.raises(ValueError) as raised_exception:
        validate_config(global_config_dict=bad_config)

    assert len(raised_exception.value.args[0]) == 2


def test_config_validation_fails_no_default_args_section(sample_config_dict):
    """
    Check that we get an exception raised if default args
    subsection missing.
    """
    bad_config = deepcopy(sample_config_dict)
    bad_config.pop("default_args")

    with pytest.raises(ValueError) as raised_exception:
        validate_config(global_config_dict=bad_config)

    assert len(raised_exception.value.args[0]) == 1


def test_config_validation_fails_bad_etl_subsection(sample_config_dict):
    """
    Check that we get an exception raised if an etl subsection
    does not contain correct keys.
    """
    bad_config = deepcopy(sample_config_dict)
    bad_config["etl"]["calls"].pop("source")

    with pytest.raises(ValueError) as raised_exception:
        validate_config(global_config_dict=bad_config)

    assert len(raised_exception.value.args[0]) == 1


def test_find_files_default_filter(tmpdir):
    """
    Test that find files returns correct files
    with default filter argument.
    """
    tmpdir.join("A.txt").write("content")
    tmpdir.join("B.txt").write("content")
    tmpdir.join("README.md").write("content")

    tmpdir_path_obj = Path(tmpdir)

    files = find_files(files_path=tmpdir_path_obj)

    assert set([file.name for file in files]) == set(["A.txt", "B.txt"])


def test_find_files_non_default_filter(tmpdir):
    """
    Test that find files returns correct files
    with non-default filter argument.
    """
    tmpdir.join("A.txt").write("content")
    tmpdir.join("B.txt").write("content")
    tmpdir.join("README.md").write("content")

    tmpdir_path_obj = Path(tmpdir)

    files = find_files(files_path=tmpdir_path_obj, ignore_filenames=["B.txt", "A.txt"])

    assert set([file.name for file in files]) == set(["README.md"])


@pytest.mark.parametrize(
    "file_name,want",
    [
        # Note: we are not testing SMS here because it is ingested from sql instead of csv
        (
            "CALLS_20160101.csv.gz",
            {"cdr_type": CDRType("calls"), "cdr_date": parse("20160101")},
        ),
        (
            "MDS_20160101.csv.gz",
            {"cdr_type": CDRType("mds"), "cdr_date": parse("20160101")},
        ),
        (
            "TOPUPS_20160101.csv.gz",
            {"cdr_type": CDRType("topups"), "cdr_date": parse("20160101")},
        ),
    ],
)
def test_parse_file_name(file_name, want, sample_config_dict):
    """
    Test we can parse cdr_type and cdr_date
    from filenames based on cdr type config.
    """
    cdr_type_config = sample_config_dict["etl"]
    got = parse_file_name(file_name=file_name, cdr_type_config=cdr_type_config)
    assert got == want


def test_parse_file_name_exception(sample_config_dict):
    """
    Test that we get a value error if filename does
    not match any pattern
    """
    cdr_type_config = sample_config_dict["etl"]
    file_name = "bob.csv"
    with pytest.raises(ValueError):
        parse_file_name(file_name=file_name, cdr_type_config=cdr_type_config)


def test_get_config_from_file(tmpdir):
    """
    Test that we can load yaml to dict from file
    """
    sample_dict = {"A": 23, "B": [1, 2, 34], "C": {"A": "bob"}}
    config_dir = tmpdir.mkdir("config")
    config_file = config_dir.join("config.yml")
    config_file.write(yaml.dump(sample_dict))

    config = get_config_from_file(config_filepath=Path(config_file))
    assert config == sample_dict
