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
