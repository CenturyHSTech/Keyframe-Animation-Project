"""
Test CSS Requirements.
"""
import pytest
from webcode_tk import css_tools as css

project_dir = "project/"

# Animation Tests (test for # of keyframes and types of transitions)
animation_report = []
animation_report = css.get_animation_report(project_dir)


def test_for_number_of_animations():
    assert len(animation_report) >= 1


def get_keyframe_results(report: list) -> dict:
    keyframe_results = {}
    for animation in report:
        filename = animation.get("file")
        if filename not in keyframe_results:
            keyframe_results[filename] = {}
            keyframe_results[filename]["froms_tos"] = 0
            keyframe_results[filename]["pct_keyframes"] = 0
        keyframes = animation.get("keyframes")
        for keyframe_data in keyframes:
            keyframe_type = keyframe_data[0]
            num_keyframes = len(keyframe_data[1])
            if keyframe_type == "percentage":
                keyframe_results[filename]["pct_keyframes"] += num_keyframes
            elif keyframe_type in ("from", "to"):
                keyframe_results[filename]["froms_tos"] += num_keyframes
    results = []
    for file, frames in keyframe_results.items():
        results.append((file, frames.get("pct_keyframes"),
                        frames.get("froms_tos")))
    return results


keyframe_results = get_keyframe_results(animation_report)


def get_keyframe_report(keyframe_results: list, pct_goal: int,
                        overall_goal: int) -> list:
    """returns a list of pass/fail messages (1 for each file)

    Args:
        keyframe_results: a list of filenames with number of percentage
            keyframes and from and to keyframes.
        pct_goal: the minimum number of percentage keyframes we would want
            to see.
        overall_goal: the total number of keyframes in case there are not
            the minimum number of percentage keyframes.

    Returns:
        results: a list of messages (one for each file in the project) with
            a pass or fail with number present of each type.
    """
    results = []
    for item in keyframe_results:
        file, pct_keyframes, from_to_keyframes = item
        msg = ""

        # first check the percentage goal
        if pct_keyframes > pct_goal:
            msg = f"pass: {file} has {pct_keyframes} percentage keyframes."
        else:
            # if that fails, check overall
            num_overall = pct_keyframes + from_to_keyframes
            if num_overall >= overall_goal:
                msg = f"pass: {file} has {num_overall} keyframes (enough "
                msg += "overall to meet)."
            else:
                msg = f"fail: {file} does not have enough keyframes to pass."
        results.append(msg)
    return results


def get_animation_properties_report(animation_values: list, num_goal: int,
                                    specific_properties=None):
    """returns a list of pass/fail messages (1 for each file)

    Since animation_values might have multiple entries for the same file,
    we need to track a per file record to see if it meets or not.

    Args:
        animation_values: a list of filenames with keyframe and property
            data.
        num_goal: the minimum number of percentage keyframes we would want
            to see.
        specific_properties: a list or tuple of properties required to be
            present.

    Returns:
        results: a list of messages (one for each file in the project) with
            a pass or fail with number present of each type.
    """
    results = []
    properties_targetted = set()
    current_file = animation_values[0].get("file")
    for item in animation_values:
        filename = item.get("file")
        if filename != current_file:
            # we are on to a new file, it's time to create a message
            if specific_properties:
                # make sure it's a list
                msg = get_targetted_properties_msg(specific_properties,
                                                   properties_targetted,
                                                   current_file)
                results.append(msg)
            else:
                # Now lets check for num of unique properties
                msg = get_num_properties_msg(num_goal, properties_targetted,
                                             current_file)
                results.append(msg)

            # now is the time to restart our list of properties
            properties_targetted = set()
            current_file = filename

        # will need to change the key on the animations_values list
        properties = item.get("values_targetted")
        for property in properties:
            # add only unique properties
            properties_targetted.add(property)

    # process the current file (now that we're done looping)
    # check to see if there are any required properties
    if specific_properties:
        # make sure it's a list
        msg = get_targetted_properties_msg(specific_properties,
                                           properties_targetted,
                                           current_file)
        results.append(msg)
    else:
        # Now lets check for num of unique properties
        msg = get_num_properties_msg(num_goal, properties_targetted,
                                     current_file)
        results.append(msg)
    return results


def get_num_properties_msg(num_goal, properties_targetted, current_file):
    num_unique_props = len(properties_targetted)
    if num_unique_props >= num_goal:
        msg = f"pass: {current_file}'s animations targetted the minimum "
        msg += "required number of properties."
    else:
        off_by = num_goal - num_unique_props
        msg = f"fail: {current_file}'s animations did not target the "
        msg += f"{num_goal} required number of properties (missing "
        msg += f"{off_by})"
    return msg


def get_targetted_properties_msg(properties, properties_targetted,
                                 current_file):
    properties = list(properties)
    for property in properties_targetted:
        if property in properties:
            properties.remove(property)
    if properties:
        # we failed to include all required properties
        msg = f"fail: {current_file}'s animations did not target all "
        msg += f"required properties (missing {properties})"
    else:
        # Success on the required properties
        msg = f"pass: {current_file}'s animations targetted all "
        msg += "required properties"
    return msg


keyframe_report = get_keyframe_report(keyframe_results, 4, 6)
animation_values_report = get_animation_properties_report(animation_report, 4)


@pytest.mark.parametrize("message", keyframe_report)
def test_project_for_keyframe_results(message):
    assert "pass" in message[:5]


@pytest.mark.parametrize("message", animation_values_report)
def test_project_for_animation_properties(message):
    assert "pass" in message[:5]
