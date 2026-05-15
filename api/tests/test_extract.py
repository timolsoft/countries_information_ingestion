import pytest
import pandas as pd
from requests.exceptions import RequestException
from unittest.mock import patch, MagicMock
import sys
import os


# Make sure Python can find extract.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from extract import extract_country_field1, extract_country_field2

# Sample API response — mimics what restcountries.com actually returns
SAMPLE_COUNTRY = {
    "name": {"common": "Germany", "official": "Federal Republic of Germany"},
    "independent": True,
    "unMember": True,
    "startOfWeek": "monday",
    "currencies": {"EUR": {"name": "Euro", "symbol": "€"}},
    "idd": {"root": "+4", "suffixes": ["9"]},
    "capital": ["Berlin"],
    "languages": {"deu": "German"},
    "region": "Europe",
    "subregion": "Western Europe",
    "area": 357114.0,
    "population": 83240525,
    "continents": ["Europe"]
}

class TestExtractField1:

    @patch('extract.requests.get')
    def test_returns_dataframe(self, mock_get):
        """extract_country_field1 should return a non-empty DataFrame"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [SAMPLE_COUNTRY]
        mock_get.return_value = mock_response

        result = extract_country_field1()

        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    @patch('extract.requests.get')
    def test_returns_expected_columns(self, mock_get):
        """DataFrame must contain all required columns"""
        mock_response = MagicMock()
        mock_response.json.return_value = [SAMPLE_COUNTRY]
        mock_get.return_value = mock_response

        result = extract_country_field1()

        expected_columns = [
            'commonName', 'officialName', 'startOfWeek',
            'independent', 'unMember', 'currencyCode',
            'currencyName', 'currencySymbol', 'idd',
            'capital', 'region', 'subregion', 'languages'
        ]
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"

    @patch('extract.requests.get')
    def test_currency_extracted_correctly(self, mock_get):
        """Currency fields should be strings not lists"""
        mock_response = MagicMock()
        mock_response.json.return_value = [SAMPLE_COUNTRY]
        mock_get.return_value = mock_response

        result = extract_country_field1()

        assert result['currencyCode'].iloc[0] == 'EUR'
        assert result['currencyName'].iloc[0] == 'Euro'
        assert result['currencySymbol'].iloc[0] == '€'

    @patch('extract.requests.get')
    def test_capital_extracted_as_string(self, mock_get):
        """Capital should be a string not a list"""
        mock_response = MagicMock()
        mock_response.json.return_value = [SAMPLE_COUNTRY]
        mock_get.return_value = mock_response

        result = extract_country_field1()

        assert result['capital'].iloc[0] == 'Berlin'
        assert isinstance(result['capital'].iloc[0], str)

    @patch('extract.requests.get')
    def test_idd_concatenated_correctly(self, mock_get):
        """IDD should be root + suffix concatenated"""
        mock_response = MagicMock()
        mock_response.json.return_value = [SAMPLE_COUNTRY]
        mock_get.return_value = mock_response

        result = extract_country_field1()

        assert result['idd'].iloc[0] == '+49'

    @patch('extract.requests.get')
    def test_returns_empty_df_on_http_error(self, mock_get):
        """Should return empty DataFrame on HTTP error, not crash"""
        mock_get.side_effect = RequestException("Connection timeout")

        result = extract_country_field1()

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    @patch('extract.requests.get')
    def test_handles_missing_currency(self, mock_get):
        """Countries with no currency should not crash the extract"""
        country_no_currency = {**SAMPLE_COUNTRY, "currencies": {}}
        mock_response = MagicMock()
        mock_response.json.return_value = [country_no_currency]
        mock_get.return_value = mock_response

        result = extract_country_field1()

        assert not result.empty
        assert result['currencyCode'].iloc[0] is None

    @patch('extract.requests.get')
    def test_handles_missing_capital(self, mock_get):
        """Countries with no capital should not crash the extract"""
        country_no_capital = {**SAMPLE_COUNTRY, "capital": []}
        mock_response = MagicMock()
        mock_response.json.return_value = [country_no_capital]
        mock_get.return_value = mock_response

        result = extract_country_field1()

        assert not result.empty
        assert result['capital'].iloc[0] is None

class TestExtractField2:

    @patch('extract.requests.get')
    def test_returns_dataframe(self, mock_get):
        """extract_country_field2 should return a non-empty DataFrame"""
        mock_response = MagicMock()
        mock_response.json.return_value = [SAMPLE_COUNTRY]
        mock_get.return_value = mock_response

        result = extract_country_field2()

        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    @patch('extract.requests.get')
    def test_returns_expected_columns(self, mock_get):
        """DataFrame must contain all required columns"""
        mock_response = MagicMock()
        mock_response.json.return_value = [SAMPLE_COUNTRY]
        mock_get.return_value = mock_response

        result = extract_country_field2()

        for col in ['nameCommon', 'area', 'population', 'continents']:
            assert col in result.columns, f"Missing column: {col}"

    @patch('extract.requests.get')
    def test_continents_extracted_as_string(self, mock_get):
        """Continents should be a string not a list"""
        mock_response = MagicMock()
        mock_response.json.return_value = [SAMPLE_COUNTRY]
        mock_get.return_value = mock_response

        result = extract_country_field2()

        assert result['continents'].iloc[0] == 'Europe'
        assert isinstance(result['continents'].iloc[0], str)

    @patch('extract.requests.get')
    def test_returns_empty_df_on_http_error(self, mock_get):
        """Should return empty DataFrame on HTTP error, not crash"""
        mock_get.side_effect = RequestException("Connection timeout")

        result = extract_country_field2()

        assert isinstance(result, pd.DataFrame)
        assert result.empty