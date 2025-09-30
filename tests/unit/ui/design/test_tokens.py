"""Tests for design tokens."""

import pytest
import yaml
from pydantic import ValidationError

from cli_patterns.ui.design.tokens import (
    CategoryToken,
    DisplayMetadata,
    DisplayStyle,
    EmphasisToken,
    HierarchyToken,
    StatusToken,
)

pytestmark = pytest.mark.design


class TestCategoryToken:
    """Test CategoryToken enum."""

    def test_all_values_are_unique(self):
        """Test that all CategoryToken values are unique."""
        values = [token.value for token in CategoryToken]
        assert len(values) == len(set(values)), "CategoryToken values must be unique"

    def test_correct_values(self):
        """Test that CategoryToken has the expected values."""
        expected_values = {
            "cat_1",
            "cat_2",
            "cat_3",
            "cat_4",
            "cat_5",
            "cat_6",
            "cat_7",
            "cat_8",
        }
        actual_values = {token.value for token in CategoryToken}
        assert actual_values == expected_values

    def test_yaml_serialization(self):
        """Test YAML serialization of CategoryToken."""
        token = CategoryToken.CAT_1
        serialized = yaml.safe_dump(token.value)
        deserialized = yaml.safe_load(serialized)
        assert deserialized == token.value

    def test_string_inheritance(self):
        """Test that CategoryToken inherits from str."""
        token = CategoryToken.CAT_1
        assert isinstance(token, str)
        assert token == "cat_1"


class TestHierarchyToken:
    """Test HierarchyToken enum."""

    def test_all_values_are_unique(self):
        """Test that all HierarchyToken values are unique."""
        values = [token.value for token in HierarchyToken]
        assert len(values) == len(set(values)), "HierarchyToken values must be unique"

    def test_correct_values(self):
        """Test that HierarchyToken has the expected values."""
        expected_values = {"primary", "secondary", "tertiary", "quaternary"}
        actual_values = {token.value for token in HierarchyToken}
        assert actual_values == expected_values

    def test_yaml_serialization(self):
        """Test YAML serialization of HierarchyToken."""
        token = HierarchyToken.PRIMARY
        serialized = yaml.safe_dump(token.value)
        deserialized = yaml.safe_load(serialized)
        assert deserialized == token.value

    def test_string_inheritance(self):
        """Test that HierarchyToken inherits from str."""
        token = HierarchyToken.PRIMARY
        assert isinstance(token, str)
        assert token == "primary"


class TestStatusToken:
    """Test StatusToken enum."""

    def test_all_values_are_unique(self):
        """Test that all StatusToken values are unique."""
        values = [token.value for token in StatusToken]
        assert len(values) == len(set(values)), "StatusToken values must be unique"

    def test_correct_values(self):
        """Test that StatusToken has the expected values."""
        expected_values = {"success", "error", "warning", "info", "muted", "running"}
        actual_values = {token.value for token in StatusToken}
        assert actual_values == expected_values

    def test_yaml_serialization(self):
        """Test YAML serialization of StatusToken."""
        token = StatusToken.SUCCESS
        serialized = yaml.safe_dump(token.value)
        deserialized = yaml.safe_load(serialized)
        assert deserialized == token.value

    def test_string_inheritance(self):
        """Test that StatusToken inherits from str."""
        token = StatusToken.SUCCESS
        assert isinstance(token, str)
        assert token == "success"


class TestEmphasisToken:
    """Test EmphasisToken enum."""

    def test_all_values_are_unique(self):
        """Test that all EmphasisToken values are unique."""
        values = [token.value for token in EmphasisToken]
        assert len(values) == len(set(values)), "EmphasisToken values must be unique"

    def test_correct_values(self):
        """Test that EmphasisToken has the expected values."""
        expected_values = {"strong", "normal", "subtle"}
        actual_values = {token.value for token in EmphasisToken}
        assert actual_values == expected_values

    def test_yaml_serialization(self):
        """Test YAML serialization of EmphasisToken."""
        token = EmphasisToken.STRONG
        serialized = yaml.safe_dump(token.value)
        deserialized = yaml.safe_load(serialized)
        assert deserialized == token.value

    def test_string_inheritance(self):
        """Test that EmphasisToken inherits from str."""
        token = EmphasisToken.STRONG
        assert isinstance(token, str)
        assert token == "strong"


class TestDisplayMetadata:
    """Test DisplayMetadata Pydantic model."""

    def test_valid_creation(self):
        """Test creating valid DisplayMetadata instances."""
        metadata = DisplayMetadata(category=CategoryToken.CAT_1)
        assert metadata.category == CategoryToken.CAT_1
        assert metadata.hierarchy == HierarchyToken.PRIMARY  # default
        assert metadata.emphasis == EmphasisToken.NORMAL  # default

    def test_with_all_fields(self):
        """Test creating DisplayMetadata with all fields specified."""
        metadata = DisplayMetadata(
            category=CategoryToken.CAT_2,
            hierarchy=HierarchyToken.SECONDARY,
            emphasis=EmphasisToken.STRONG,
        )
        assert metadata.category == CategoryToken.CAT_2
        assert metadata.hierarchy == HierarchyToken.SECONDARY
        assert metadata.emphasis == EmphasisToken.STRONG

    def test_validation_error_invalid_category(self):
        """Test validation error with invalid category."""
        with pytest.raises(ValidationError) as exc_info:
            DisplayMetadata(category="invalid_category")

        error = exc_info.value
        assert "category" in str(error)

    def test_validation_error_invalid_hierarchy(self):
        """Test validation error with invalid hierarchy."""
        with pytest.raises(ValidationError) as exc_info:
            DisplayMetadata(category=CategoryToken.CAT_1, hierarchy="invalid_hierarchy")

        error = exc_info.value
        assert "hierarchy" in str(error)

    def test_validation_error_invalid_emphasis(self):
        """Test validation error with invalid emphasis."""
        with pytest.raises(ValidationError) as exc_info:
            DisplayMetadata(category=CategoryToken.CAT_1, emphasis="invalid_emphasis")

        error = exc_info.value
        assert "emphasis" in str(error)

    def test_with_status_method(self):
        """Test with_status method creates proper DisplayStyle."""
        metadata = DisplayMetadata(
            category=CategoryToken.CAT_3,
            hierarchy=HierarchyToken.TERTIARY,
            emphasis=EmphasisToken.SUBTLE,
        )

        style = metadata.with_status(StatusToken.SUCCESS)

        assert isinstance(style, DisplayStyle)
        assert style.category == CategoryToken.CAT_3
        assert style.hierarchy == HierarchyToken.TERTIARY
        assert style.emphasis == EmphasisToken.SUBTLE
        assert style.status == StatusToken.SUCCESS

    def test_with_status_preserves_all_fields(self):
        """Test that with_status preserves all original fields."""
        metadata = DisplayMetadata(category=CategoryToken.CAT_4)
        style = metadata.with_status(StatusToken.ERROR)

        assert style.category == metadata.category
        assert style.hierarchy == metadata.hierarchy
        assert style.emphasis == metadata.emphasis
        assert style.status == StatusToken.ERROR

    def test_yaml_serialization(self):
        """Test YAML serialization of DisplayMetadata."""
        metadata = DisplayMetadata(
            category=CategoryToken.CAT_1,
            hierarchy=HierarchyToken.SECONDARY,
            emphasis=EmphasisToken.STRONG,
        )

        # Convert to dict with mode='json' to serialize enums as strings
        data = metadata.model_dump(mode="json")
        serialized = yaml.safe_dump(data)
        deserialized = yaml.safe_load(serialized)

        # Recreate from deserialized data
        restored = DisplayMetadata(**deserialized)
        assert restored == metadata


class TestDisplayStyle:
    """Test DisplayStyle Pydantic model."""

    def test_valid_creation_without_status(self):
        """Test creating valid DisplayStyle without status."""
        style = DisplayStyle(
            category=CategoryToken.CAT_5,
            hierarchy=HierarchyToken.QUATERNARY,
            emphasis=EmphasisToken.SUBTLE,
        )

        assert style.category == CategoryToken.CAT_5
        assert style.hierarchy == HierarchyToken.QUATERNARY
        assert style.emphasis == EmphasisToken.SUBTLE
        assert style.status is None

    def test_valid_creation_with_status(self):
        """Test creating valid DisplayStyle with status."""
        style = DisplayStyle(
            category=CategoryToken.CAT_6,
            hierarchy=HierarchyToken.PRIMARY,
            emphasis=EmphasisToken.NORMAL,
            status=StatusToken.WARNING,
        )

        assert style.category == CategoryToken.CAT_6
        assert style.hierarchy == HierarchyToken.PRIMARY
        assert style.emphasis == EmphasisToken.NORMAL
        assert style.status == StatusToken.WARNING

    def test_validation_error_missing_required_field(self):
        """Test validation error when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            DisplayStyle(
                hierarchy=HierarchyToken.PRIMARY, emphasis=EmphasisToken.NORMAL
            )

        error = exc_info.value
        assert "category" in str(error)

    def test_validation_error_invalid_status(self):
        """Test validation error with invalid status."""
        with pytest.raises(ValidationError) as exc_info:
            DisplayStyle(
                category=CategoryToken.CAT_1,
                hierarchy=HierarchyToken.PRIMARY,
                emphasis=EmphasisToken.NORMAL,
                status="invalid_status",
            )

        error = exc_info.value
        assert "status" in str(error)

    def test_from_metadata_classmethod_without_status(self):
        """Test from_metadata classmethod without status."""
        metadata = DisplayMetadata(
            category=CategoryToken.CAT_7,
            hierarchy=HierarchyToken.SECONDARY,
            emphasis=EmphasisToken.STRONG,
        )

        style = DisplayStyle.from_metadata(metadata)

        assert style.category == metadata.category
        assert style.hierarchy == metadata.hierarchy
        assert style.emphasis == metadata.emphasis
        assert style.status is None

    def test_from_metadata_classmethod_with_status(self):
        """Test from_metadata classmethod with status."""
        metadata = DisplayMetadata(
            category=CategoryToken.CAT_8,
            hierarchy=HierarchyToken.TERTIARY,
            emphasis=EmphasisToken.SUBTLE,
        )

        style = DisplayStyle.from_metadata(metadata, StatusToken.RUNNING)

        assert style.category == metadata.category
        assert style.hierarchy == metadata.hierarchy
        assert style.emphasis == metadata.emphasis
        assert style.status == StatusToken.RUNNING

    def test_from_metadata_with_defaults(self):
        """Test from_metadata with DisplayMetadata defaults."""
        metadata = DisplayMetadata(category=CategoryToken.CAT_1)
        style = DisplayStyle.from_metadata(metadata, StatusToken.INFO)

        assert style.category == CategoryToken.CAT_1
        assert style.hierarchy == HierarchyToken.PRIMARY
        assert style.emphasis == EmphasisToken.NORMAL
        assert style.status == StatusToken.INFO

    def test_yaml_serialization(self):
        """Test YAML serialization of DisplayStyle."""
        style = DisplayStyle(
            category=CategoryToken.CAT_2,
            hierarchy=HierarchyToken.SECONDARY,
            emphasis=EmphasisToken.STRONG,
            status=StatusToken.SUCCESS,
        )

        # Convert to dict with mode='json' to serialize enums as strings
        data = style.model_dump(mode="json")
        serialized = yaml.safe_dump(data)
        deserialized = yaml.safe_load(serialized)

        # Recreate from deserialized data
        restored = DisplayStyle(**deserialized)
        assert restored == style


class TestIntegration:
    """Integration tests across all token components."""

    def test_complete_workflow(self):
        """Test complete workflow from metadata to styled display."""
        # Create base metadata
        metadata = DisplayMetadata(
            category=CategoryToken.CAT_1,
            hierarchy=HierarchyToken.SECONDARY,
            emphasis=EmphasisToken.STRONG,
        )

        # Create style with status using with_status method
        success_style = metadata.with_status(StatusToken.SUCCESS)

        # Create style using from_metadata classmethod
        error_style = DisplayStyle.from_metadata(metadata, StatusToken.ERROR)

        # Verify both approaches work correctly
        assert success_style.category == metadata.category
        assert success_style.status == StatusToken.SUCCESS

        assert error_style.category == metadata.category
        assert error_style.status == StatusToken.ERROR

        # Both should have same base properties
        assert success_style.hierarchy == error_style.hierarchy
        assert success_style.emphasis == error_style.emphasis

    def test_all_enum_combinations(self):
        """Test that all enum combinations can be used together."""
        for category in CategoryToken:
            for hierarchy in HierarchyToken:
                for emphasis in EmphasisToken:
                    for status in StatusToken:
                        # Test DisplayStyle creation
                        style = DisplayStyle(
                            category=category,
                            hierarchy=hierarchy,
                            emphasis=emphasis,
                            status=status,
                        )

                        assert style.category == category
                        assert style.hierarchy == hierarchy
                        assert style.emphasis == emphasis
                        assert style.status == status

    def test_edge_case_empty_status(self):
        """Test edge case with None status in various contexts."""
        metadata = DisplayMetadata(category=CategoryToken.CAT_1)

        # Test DisplayStyle.from_metadata with None status
        style1 = DisplayStyle.from_metadata(metadata, None)
        assert style1.status is None

        # Test DisplayStyle direct creation with None status
        style2 = DisplayStyle(
            category=CategoryToken.CAT_1,
            hierarchy=HierarchyToken.PRIMARY,
            emphasis=EmphasisToken.NORMAL,
            status=None,
        )
        assert style2.status is None

        # Both should be equivalent
        assert style1 == style2

    def test_model_equality(self):
        """Test model equality comparisons."""
        metadata1 = DisplayMetadata(category=CategoryToken.CAT_1)
        metadata2 = DisplayMetadata(category=CategoryToken.CAT_1)
        metadata3 = DisplayMetadata(category=CategoryToken.CAT_2)

        assert metadata1 == metadata2
        assert metadata1 != metadata3

        style1 = DisplayStyle(
            category=CategoryToken.CAT_1,
            hierarchy=HierarchyToken.PRIMARY,
            emphasis=EmphasisToken.NORMAL,
        )
        style2 = DisplayStyle(
            category=CategoryToken.CAT_1,
            hierarchy=HierarchyToken.PRIMARY,
            emphasis=EmphasisToken.NORMAL,
        )

        assert style1 == style2
