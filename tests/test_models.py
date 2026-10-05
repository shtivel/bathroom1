from bathroom_grader.models import BathroomType


def test_bathroom_type_is_string_valued():
    # BathroomType is a StrEnum, so it should compare equal to plain strings -
    # this is what lets it serialize cleanly to/from JSON in the API.
    assert BathroomType.WOMEN == "women"


def test_bathroom_type_has_expected_members():
    assert {member.value for member in BathroomType} == {
        "women",
        "men",
        "unisex_or_family",
        "accessible",
        "other",
    }
