"""
Test CSS Requirements.
"""
import pytest
from webcode_tk import animation_tools

project_dir = "project/"

# Animation Tests (test for # of keyframes and types of transitions)


animation_report = []
animation_report = animation_tools.get_animation_report(project_dir)


def test_for_number_of_animations():
    assert len(animation_report) >= 1


keyframe_data = animation_tools.get_keyframe_report(project_dir, 6, 4)


@pytest.mark.parametrize("results", keyframe_data)
def test_for_4_percent_or_6_overall_keyframes(results):
    assert "pass:" in results


animation_properties_data = animation_tools.get_animation_properties_report(
    project_dir, 4)


@pytest.mark.parametrize("results", animation_properties_data)
def test_for_four_unique_animation_properties(results):
    assert "pass:" in results
