"""This is the testing module for machine_learning_client"""

from unittest.mock import patch, MagicMock
from PIL import Image
import pytest
from machine_learning_client import mlc, connection, main, pytesseract


@pytest.fixture(name="example")
def example_image():
    """This is the example image used for testing, image will be kept under the same directory"""
    # Create a real image object using a BytesIO instance
    with patch("machine_learning_client.Image.open") as mock_open:
        mock_bytesio_instance = MagicMock()
        mock_open.return_value = Image.open(mock_bytesio_instance)

        # Read the image file and encode it in base64
        with open("testcase.jpg", "rb") as image_file:
            image_data = image_file.read()

        # Return the actual image data
        return image_data


def test_mlc_with_valid_image(example):
    """This is the test of valid image"""
    # Call the mlc function with actual image data
    title, content = mlc(example)
    # Assertions
    assert title == "This is a test case for MLC"
    # pylint: disable=line-too-long
    assert (
        content
        == "\nThis is a test case for MLC This is a test case for MLC This is a test case for MLC\n"
    )


def test_mlc_with_invalid_image(example):
    """This is for invalid image"""
    # pylint: disable=line-too-long
    with patch(
        "machine_learning_client.pytesseract.image_to_string",
        side_effect=pytesseract.TesseractError(
            status=1, message="Mocked TesseractError"
        ),
    ):
        # Call the mlc function with invalid image data
        title, content = mlc(example)
        # Assertions
        assert title == "Cannot recognize title!"
        assert content == "Cannot recognize main body!"


def test_connection_with_example_image(example):
    """Testing connection..."""
    # Mocking MongoClient and Collection
    # pylint: disable=unused-variable
    with patch("pymongo.MongoClient") as mock_client:
        with patch("pymongo.collection.Collection") as mock_collection:
            # Mocking find_one to return a document with raw_image field
            mock_collection.find_one.return_value = {
                "_id": "some_id",
                "raw_image": example,
            }
            # Call the connection function for testing
            connection(
                flag=False
            )  # Set flag to False to exit the loop after one iteration


def test_mlc_with_exception(example):
    """Testing nlc() exception handling"""
    # Mock the pytesseract.image_to_string function to raise an exception
    # pylint: disable=line-too-long
    with patch(
        "machine_learning_client.pytesseract.image_to_string",
        side_effect=pytesseract.TesseractError(
            status=1, message="Mocked TesseractError"
        ),
    ):
        title, content = mlc(example)
        # Assertions
        assert title == "Cannot recognize title!"
        assert content == "Cannot recognize main body!"


def test_mlc_with_empty_image(example):
    """Empty image handling"""
    # Mock the pytesseract.image_to_string function to return an empty string
    with patch("machine_learning_client.pytesseract.image_to_string", return_value=""):
        title, content = mlc(example)
        # Assertions
        assert title == "Cannot recognize title!"
        assert content == "Cannot recognize main body!"


def test_mlc_with_multi_line_text(example):
    """When the line code is multiple lines"""
    # Mock the pytesseract.image_to_string function to return multi-line text
    # pylint: disable=line-too-long
    with patch(
        "machine_learning_client.pytesseract.image_to_string",
        return_value="Line 1\nLine 2\nLine 3",
    ):
        title, content = mlc(example)
        # Assertions
        assert title == "Line 1"
        assert content == "Line 2\nLine 3"


def test_mlc_with_invalid_image_format():
    """When there is a wroing image format, error handling"""
    # Call mlc with image data in an invalid format (e.g., not an image)
    title, content = mlc(b"InvalidImageData")
    # Assertions
    assert title == "ERROR in raw_image format!"
    assert content == "ERROR in raw_image format!"


def test_main_with_flag_true():
    """When the flag for running is true"""
    with patch("machine_learning_client.connection") as mock_connection:
        main(flag=True)
        mock_connection.assert_called_once_with(True)


def test_main_with_flag_false():
    """When the flag for running is false"""
    with patch("machine_learning_client.connection") as mock_connection:
        main(flag=False)
        mock_connection.assert_called_once_with(False)


# Run the tests with coverage using: pytest --cov=machine_learning_client --cov-report term-missing test_machine_learning_client.py