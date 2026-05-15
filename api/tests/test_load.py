import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from load import validate_dataframes, build_country_dataframe

# ── Sample data ────────────────────────────────────────────────────

SAMPLE_FIELD1 = pd.DataFrame([{
    'commonName':     'Germany',
    'officialName':   'Federal Republic of Germany',
    'startOfWeek':    'monday',
    'independent':    True,
    'unMember':       True,
    'currencyCode':   'EUR',
    'currencyName':   'Euro',
    'currencySymbol': '€',
    'idd':            '+49',
    'capital':        'Berlin',
    'region':         'Europe',
    'subregion':      'Western Europe',
    'languages':      'German',
}])

SAMPLE_FIELD2 = pd.DataFrame([{
    'nameCommon':  'Germany',
    'area':        357114.0,
    'population':  83240525,
    'continents':  'Europe',
}])


# ── validate_dataframes tests ───────────────────────────────────────

class TestValidateDataframes:

    def test_passes_with_valid_data(self):
        """Should return True when both DataFrames have data"""
        result = validate_dataframes(SAMPLE_FIELD1, SAMPLE_FIELD2)
        assert result is True

    def test_fails_when_field1_empty(self):
        """Should return False when field1 is empty"""
        result = validate_dataframes(pd.DataFrame(), SAMPLE_FIELD2)
        assert result is False

    def test_fails_when_field2_empty(self):
        """Should return False when field2 is empty"""
        result = validate_dataframes(SAMPLE_FIELD1, pd.DataFrame())
        assert result is False

    def test_fails_when_both_empty(self):
        """Should return False when both are empty"""
        result = validate_dataframes(pd.DataFrame(), pd.DataFrame())
        assert result is False


# ── build_country_dataframe tests ──────────────────────────────────

class TestBuildCountryDataframe:

    def test_returns_dataframe(self):
        """Should return a DataFrame"""
        result = build_country_dataframe(SAMPLE_FIELD1, SAMPLE_FIELD2)
        assert isinstance(result, pd.DataFrame)

    def test_merge_produces_correct_row_count(self):
        """Merged DataFrame should have same rows as input"""
        result = build_country_dataframe(SAMPLE_FIELD1, SAMPLE_FIELD2)
        assert len(result) == 1

    def test_nameCommon_column_dropped(self):
        """nameCommon should be dropped after merge"""
        result = build_country_dataframe(SAMPLE_FIELD1, SAMPLE_FIELD2)
        assert 'nameCommon' not in result.columns

    def test_countryId_column_exists(self):
        """countryId surrogate key should be generated"""
        result = build_country_dataframe(SAMPLE_FIELD1, SAMPLE_FIELD2)
        assert 'countryId' in result.columns

    def test_countryId_starts_at_one(self):
        """countryId should start at 1 not 0"""
        result = build_country_dataframe(SAMPLE_FIELD1, SAMPLE_FIELD2)
        assert result['countryId'].iloc[0] == 1

    def test_all_columns_present(self):
        """Merged DataFrame should contain all expected columns"""
        result = build_country_dataframe(SAMPLE_FIELD1, SAMPLE_FIELD2)
        expected = [
            'commonName', 'officialName', 'region', 'subregion',
            'currencyCode', 'capital', 'population', 'area',
            'continents', 'countryId'
        ]
        for col in expected:
            assert col in result.columns, f"Missing column: {col}"

    def test_unmatched_countries_excluded(self):
        """Countries that dont match between field1 and field2 should be excluded"""
        field2_different = pd.DataFrame([{
            'nameCommon':  'France',
            'area':        551695.0,
            'population':  67391582,
            'continents':  'Europe',
        }])
        result = build_country_dataframe(SAMPLE_FIELD1, field2_different)
        assert len(result) == 0
        