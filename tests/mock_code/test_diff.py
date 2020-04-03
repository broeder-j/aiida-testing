# -*- coding: utf-8 -*-
"""
Test basic usage of the mock code on examples using aiida-diff.
"""

import os
import tempfile
from aiida.engine import run_get_node
from aiida.plugins import CalculationFactory

CALC_ENTRY_POINT = 'diff'

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def check_diff_output(result):
    """
    Checks the result from a diff calculation against a reference.
    """
    diff_res_lines = tuple([
        line.strip() for line in result['diff'].get_content().splitlines() if line.strip()
    ])
    assert diff_res_lines == (
        "1,2c1", "< Lorem ipsum dolor..", "<", "---",
        "> Please report to the ministry of silly walks."
    )


def test_basic(mock_code_factory, generate_diff_inputs):
    """
    Check that mock code takes data from cache, if inputs are recognized.
    """
    mock_code = mock_code_factory(
        label='diff',
        data_dir_abspath=TEST_DATA_DIR,
        entry_point=CALC_ENTRY_POINT,
        ignore_files=('_aiidasubmit.sh', 'file*txt')
    )

    res, node = run_get_node(
        CalculationFactory(CALC_ENTRY_POINT), code=mock_code, **generate_diff_inputs()
    )
    assert node.exit_status == 0, "diff calculation failed with exit status {}".format(
        node.exit_status
    )
    assert node.is_finished_ok
    check_diff_output(res)


def test_inexistent_data(mock_code_factory, generate_diff_inputs):
    """
    Check that the mock code runs external executable if there is no existing data.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        mock_code = mock_code_factory(
            label='diff',
            data_dir_abspath=temp_dir,
            entry_point=CALC_ENTRY_POINT,
            ignore_files=('_aiidasubmit.sh', 'file*txt')
        )

        res, node = run_get_node(
            CalculationFactory(CALC_ENTRY_POINT), code=mock_code, **generate_diff_inputs()
        )
        assert node.is_finished_ok
        check_diff_output(res)


def test_broken_code(mock_code_factory, generate_diff_inputs):
    """
    Check that the mock code works also when no executable is given, if the result exists already.
    """
    mock_code = mock_code_factory(
        label='diff-broken',
        data_dir_abspath=TEST_DATA_DIR,
        entry_point=CALC_ENTRY_POINT,
        ignore_files=('_aiidasubmit.sh', 'file?.txt')
    )

    res, node = run_get_node(
        CalculationFactory(CALC_ENTRY_POINT), code=mock_code, **generate_diff_inputs()
    )
    assert node.is_finished_ok
    check_diff_output(res)


def test_broken_code_require(mock_code_factory):
    """
    Check that the mock code raises, if executable path is required but not provided.
    """

    with pytest.raises(ValueError):
        mock_code_factory(
            label='diff-broken',
            data_dir_abspath=TEST_DATA_DIR,
            entry_point=CALC_ENTRY_POINT,
            ignore_files=('_aiidasubmit.sh', 'file?.txt'),
            _config_action='require',
        )


def test_broken_code_generate(mock_code_factory, testing_config):
    """
    Check that mock code adds missing key to testing config, when asked to 'generate'.
    """
    mock_code_factory(
        label='diff-broken',
        data_dir_abspath=TEST_DATA_DIR,
        entry_point=CALC_ENTRY_POINT,
        ignore_files=('_aiidasubmit.sh', 'file?.txt'),
        _config_action='generate',
    )
    assert 'diff-broken' in testing_config.get('mock_code')


def test_regenerate_test_data(mock_code_factory, generate_diff_inputs):  # pylint: disable=redefined-outer-name
    """
    Check that mock code regenerates test data if asked to do so.

    Note: So far, this only tests that the test still runs fine.
    Should e.g. check timestamp on test data directory.
    """
    mock_code = mock_code_factory(
        label='diff',
        data_dir_abspath=TEST_DATA_DIR,
        entry_point=CALC_ENTRY_POINT,
        ignore_files=('_aiidasubmit.sh', ),
        _regenerate_test_data=True,
    )

    res, node = run_get_node(
        CalculationFactory(CALC_ENTRY_POINT), code=mock_code, **generate_diff_inputs()
    )
    assert node.is_finished_ok
    check_diff_output(res)
