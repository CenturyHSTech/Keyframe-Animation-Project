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


keyframe_data = animation_tools.get_keyframe_report(project_dir, 6, 4, 0)
for item in keyframe_data:
    print(item)