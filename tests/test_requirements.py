"""
Test CSS Requirements.
"""
import pytest
import file_clerk.clerk as clerk
from webcode_tk import html_tools as html
from webcode_tk import css_tools as css
from webcode_tk import validator_tools as validator

project_dir = "project/"

# Test for HTML requirements
all_html_files = html.get_all_html_files(project_dir)

# List of required elements (per web page)
required_elements = [("doctype", 1),
                     ("html", 1),
                     ("head", 1),
                     ("title", 1),
                     ("h1", 1),
                     ("main", 1)]

min_required_elements = [("img", 1),]

exact_number_of_elements = html.get_number_of_elements_per_file(
    project_dir, required_elements
)
min_number_of_elements = html.get_number_of_elements_per_file(
    project_dir, min_required_elements
)
html_validation_results = validator.get_project_validation(project_dir)


@pytest.fixture
def html_files():
    html_files = html.get_all_html_files(project_dir)
    return html_files


def test_has_index_file(html_files):
    assert "project/index.html" in html_files


def test_has_css_file():
    has_style_sheet = False
    all_files = clerk.get_all_files_of_type(project_dir, "css")
    has_style_sheet = all_files
    assert has_style_sheet


@pytest.mark.parametrize("file,element,num", exact_number_of_elements)
def test_files_for_exact_number_of_elements(file, element, num):
    if not html_files:
        assert False
    actual = html.get_num_elements_in_file(element, file)
    assert actual == num


@pytest.mark.parametrize("file,element,num", min_number_of_elements)
def test_files_for_minimum_number_of_elements(file, element, num):
    if not html_files:
        assert False
    if "or" in element.lower():
        elements = element.split()
        actual = 0
        for el in elements:
            el = el.strip()
            actual += html.get_num_elements_in_file(el, file)
    else:
        actual = html.get_num_elements_in_file(element, file)
    assert actual >= num


def test_passes_html_validation(html_files):
    errors = []
    if not html_files:
        assert "html files" in html_files
    for file in html_files:
        results = validator.get_markup_validity(file)
        for result in results:
            errors.append(result.get("message"))
    assert not errors


def test_number_of_image_files_for_proficient():
    image_files = []
    image_files += clerk.get_all_files_of_type(project_dir, "jpg")
    image_files += clerk.get_all_files_of_type(project_dir, "png")
    image_files += clerk.get_all_files_of_type(project_dir, "gif")
    image_files += clerk.get_all_files_of_type(project_dir, "webp")
    assert len(image_files) >= 1


# Test CSS stuff
css_validation_results = validator.get_project_validation(
    project_dir, "css"
)

style_attributes_in_project = css.no_style_attributes_allowed_report(
    project_dir)
css_validation_results = validator.get_project_validation(
    project_dir, "css"
)

applying_styles_results = css.styles_applied_report(project_dir)


@pytest.mark.parametrize("results", style_attributes_in_project)
def test_css_for_no_style_attributes(results):
    assert "pass" == results[:4]


@pytest.mark.parametrize("results", css_validation_results)
def test_css_validation(results):
    assert "pass" == results[:4]


@pytest.mark.parametrize("results", applying_styles_results)
def test_if_file_applies_styles(results):
    assert "pass" == results[:4]


applied_properties_goals = {
        "img": {
            "properties": ("animation", ),
        }
    }

applied_properties_report = css.get_properties_applied_report(
    project_dir,
    applied_properties_goals)


@pytest.mark.parametrize("results", applied_properties_report)
def test_figure_styles_applied(results):
    assert "fail:" not in results[:5]


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
