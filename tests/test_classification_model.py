import pytest
from pydantic import ValidationError

from app.workflow.agents.classification_agent import IndustryCategory, ClassificationResult


class TestIndustryCategory:
    """测试 IndustryCategory 枚举"""

    def test_valid_value_from_string(self):
        """测试 IndustryCategory("汽车零部件") 应该有效"""
        category = IndustryCategory("汽车零部件")
        assert category == IndustryCategory.AUTO_PARTS

    def test_enum_value_mapping(self):
        """测试 IndustryCategory.AUTO_PARTS.value == "汽车零部件" """
        assert IndustryCategory.AUTO_PARTS.value == "汽车零部件"
        assert IndustryCategory.BIOMEDICAL.value == "生物医药"
        assert IndustryCategory.HARDWARE_MOLD.value == "五金模具"
        assert IndustryCategory.CHEMICAL.value == "化工"
        assert IndustryCategory.OTHER.value == "其他"

    def test_invalid_value_raises_error(self):
        """测试 IndustryCategory("无效行业") 应该抛出 ValueError"""
        with pytest.raises(ValueError):
            IndustryCategory("无效行业")

    def test_invalid_type_raises_error(self):
        """测试传入非字符串类型"""
        with pytest.raises(ValueError):
            IndustryCategory(123)


class TestClassificationResultValid:
    """测试 ClassificationResult 有效输入"""

    def test_basic_valid_input(self):
        """测试 ClassificationResult(category=IndustryCategory.AUTO_PARTS, confidence=0.95) 应该通过验证"""
        result = ClassificationResult(
            category=IndustryCategory.AUTO_PARTS,
            confidence=0.95
        )
        assert result.category == IndustryCategory.AUTO_PARTS
        assert result.confidence == 0.95

    def test_boundary_zero_confidence(self):
        """测试 ClassificationResult(category=IndustryCategory.OTHER, confidence=0.0) 边界值有效"""
        result = ClassificationResult(
            category=IndustryCategory.OTHER,
            confidence=0.0
        )
        assert result.category == IndustryCategory.OTHER
        assert result.confidence == 0.0

    def test_boundary_one_confidence(self):
        """测试 ClassificationResult(category=IndustryCategory.BIOMEDICAL, confidence=1.0) 边界值有效"""
        result = ClassificationResult(
            category=IndustryCategory.BIOMEDICAL,
            confidence=1.0
        )
        assert result.category == IndustryCategory.BIOMEDICAL
        assert result.confidence == 1.0

    def test_string_category_valid(self):
        """测试使用字符串作为 category 应该可以通过验证"""
        result = ClassificationResult(
            category="汽车零部件",
            confidence=0.95
        )
        assert result.category == IndustryCategory.AUTO_PARTS


class TestClassificationResultInvalid:
    """测试 ClassificationResult 无效输入"""

    def test_negative_confidence_raises_error(self):
        """测试 confidence=-0.1 应该抛出 ValidationError"""
        with pytest.raises(ValidationError):
            ClassificationResult(
                category=IndustryCategory.AUTO_PARTS,
                confidence=-0.1
            )

    def test_over_one_confidence_raises_error(self):
        """测试 confidence=1.1 应该抛出 ValidationError"""
        with pytest.raises(ValidationError):
            ClassificationResult(
                category=IndustryCategory.AUTO_PARTS,
                confidence=1.1
            )

    def test_invalid_category_string_raises_error(self):
        """测试 category="无效值" (非枚举) 应该抛出 ValidationError"""
        with pytest.raises(ValidationError):
            ClassificationResult(
                category="无效值",
                confidence=0.95
            )

    def test_invalid_category_type_raises_error(self):
        """测试 category 为非字符串、非枚举类型"""
        with pytest.raises(ValidationError):
            ClassificationResult(
                category=123,
                confidence=0.95
            )

    def test_missing_category_raises_error(self):
        """测试缺少 category 字段"""
        with pytest.raises(ValidationError):
            ClassificationResult(confidence=0.95)

    def test_missing_confidence_raises_error(self):
        """测试缺少 confidence 字段"""
        with pytest.raises(ValidationError):
            ClassificationResult(category=IndustryCategory.AUTO_PARTS)


class TestSerialization:
    """测试序列化"""

    def test_model_dump_returns_dict(self):
        """测试 result.model_dump() 应该返回包含 'category' 和 'confidence' 的字典"""
        result = ClassificationResult(
            category=IndustryCategory.AUTO_PARTS,
            confidence=0.95
        )
        dumped = result.model_dump()

        assert isinstance(dumped, dict)
        assert 'category' in dumped
        assert 'confidence' in dumped

    def test_category_serialization(self):
        """测试 category 可以是枚举值或字符串"""
        result = ClassificationResult(
            category=IndustryCategory.AUTO_PARTS,
            confidence=0.95
        )
        dumped = result.model_dump()

        assert dumped['category'] in [IndustryCategory.AUTO_PARTS, "汽车零部件"]

    def test_confidence_serialization(self):
        """测试 confidence 是 float"""
        result = ClassificationResult(
            category=IndustryCategory.BIOMEDICAL,
            confidence=0.5
        )
        dumped = result.model_dump()

        assert isinstance(dumped['confidence'], float)
        assert dumped['confidence'] == 0.5

    def test_model_dump_mode(self):
        """测试不同的 dump 模式"""
        result = ClassificationResult(
            category=IndustryCategory.AUTO_PARTS,
            confidence=0.95
        )

        default_dump = result.model_dump()
        json_dump = result.model_dump(mode='json')

        assert 'category' in default_dump
        assert 'category' in json_dump
