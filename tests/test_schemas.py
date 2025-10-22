import pytest
from pydantic import ValidationError
from datetime import datetime
from database.schemas import NewsMetadata


def test_news_metadata_successful_creation():
    """
    Tests that a NewsMetadata object can be created successfully with valid data.
    """
    now = datetime.now()
    news_data = {
        "title": "AI Takes Over the World",
        "published_at": now,
        "news_link": "https://example.com/news/ai-takes-over",
        "image_link": "https://example.com/images/ai.jpg",
        "extracted_at": now,
        "news_id": "12345",
    }

    news_metadata = NewsMetadata(**news_data)

    assert news_metadata.title == "AI Takes Over the World"
    assert news_metadata.published_at == now
    assert news_metadata.news_link == "https://example.com/news/ai-takes-over"
    assert news_metadata.image_link == "https://example.com/images/ai.jpg"
    assert news_metadata.extracted_at == now
    assert news_metadata.news_id == "12345"


def test_string_normalizer():
    """
    Tests that the STRING_NORMALIZER correctly strips leading/trailing whitespace.
    """
    now = datetime.now()
    news_data = {
        "title": "  A Padded Title  ",
        "published_at": now,
        "news_link": "  https://example.com/padded-link  ",
    }

    news_metadata = NewsMetadata(**news_data)

    assert news_metadata.title == "A Padded Title"
    assert news_metadata.news_link == "https://example.com/padded-link"


def test_invalid_url_pattern():
    """
    Tests that a ValidationError is raised for invalid URL patterns.
    """
    now = datetime.now()
    invalid_news_link_data = {
        "title": "Invalid Link",
        "published_at": now,
        "news_link": "htp:/invalid-link",
    }

    with pytest.raises(ValidationError):
        NewsMetadata(**invalid_news_link_data)

    invalid_image_link_data = {
        "title": "Invalid Image Link",
        "published_at": now,
        "news_link": "https://example.com/valid",
        "image_link": "ftp://invalid.com/image.jpg",
    }

    with pytest.raises(ValidationError):
        NewsMetadata(**invalid_image_link_data)


def test_datetime_serialization():
    """
    Tests that the datetime fields are serialized to the correct string format.
    """
    now = datetime.now()
    news_data = {
        "title": "Datetime Test",
        "published_at": now,
        "extracted_at": now,
        "news_link": "https://example.com/datetime-test",
    }

    news_metadata = NewsMetadata(**news_data)

    # model_dump serializes the model to a dictionary
    serialized_data = news_metadata.model_dump()

    expected_format = now.strftime(r"%Y-%m-%d %H:%M:%S")
    assert serialized_data["published_at"] == expected_format
    assert serialized_data["extracted_at"] == expected_format


def test_optional_and_default_fields():
    """
    Tests the behavior of fields with default or optional values.
    """
    now = datetime.now()
    minimal_data = {
        "title": "Minimal Data",
        "published_at": now,
        "news_link": "https://example.com/minimal",
    }

    news_metadata = NewsMetadata(**minimal_data)

    assert news_metadata.news_id is None
    assert news_metadata.image_link is None
    assert news_metadata.extracted_at is None


def test_serialization_with_none_datetime():
    """
    Tests that serializing the model works correctly when optional datetime fields are None.
    """
    now = datetime.now()
    news_data = {
        "title": "Serialization with None",
        "published_at": now,
        "news_link": "https://example.com/serialization-none",
        "extracted_at": None,  # Explicitly set to None
    }

    with pytest.raises(ValidationError) as excinfo:
        news_metadata = NewsMetadata(**news_data)
        news_metadata.model_dump()

    assert "Input should be a valid datetime" in str(excinfo.value)


def test_empty_strings_validation():
    """
    Tests that a ValidationError is raised for empty strings in required fields.
    """
    now = datetime.now()
    with pytest.raises(ValidationError) as excinfo:
        NewsMetadata(
            title="", published_at=now, news_link="https://example.com/empty-title"
        )
    assert "String should have at least 1 character" in str(excinfo.value)


def test_missing_required_fields():
    """
    Tests that a ValidationError is raised if required fields are missing.
    """
    now = datetime.now()
    # Missing 'title'
    with pytest.raises(ValidationError):
        NewsMetadata(published_at=now, news_link="https://example.com/missing-title")

    # Missing 'published_at'
    with pytest.raises(ValidationError):
        NewsMetadata(
            title="Missing Published At",
            news_link="https://example.com/missing-published-at",
        )

    # Missing 'news_link'
    with pytest.raises(ValidationError):
        NewsMetadata(title="Missing News Link", published_at=now)
