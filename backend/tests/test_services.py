import pytest
from app.services.excel_handler import ExcelHandler
import polars as pl
import tempfile
from pathlib import Path


def test_read_excel():
    """Test reading Excel file"""
    # Create test Excel file
    df = pl.DataFrame({
        "Issue": ["Issue 1", "Issue 2", ""],
        "Description": ["Desc 1", "Desc 2", "Desc 3"]
    })
    
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Write Excel
        df.write_excel(tmp_path, worksheet="TestSheet")
        
        # Read Excel
        handler = ExcelHandler()
        result_df = handler.read_excel(tmp_path, "TestSheet")
        
        assert len(result_df) == 3
        assert "Issue" in result_df.columns
        assert "Description" in result_df.columns
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_add_classification_columns():
    """Test adding classification columns"""
    df = pl.DataFrame({
        "Issue": ["Issue 1", "Issue 2"],
        "Description": ["Desc 1", "Desc 2"]
    })
    
    classifications = [
        {"불량명": "불량A", "설비명": "설비1", "조치내용": "조치1"},
        {"불량명": "불량B", "설비명": "설비2", "조치내용": "조치2"}
    ]
    
    handler = ExcelHandler()
    result_df = handler.add_classification_columns(df, classifications)
    
    assert "불량명" in result_df.columns
    assert "설비명" in result_df.columns
    assert "조치내용" in result_df.columns
    assert len(result_df) == 2
    assert result_df["불량명"][0] == "불량A"
    assert result_df["설비명"][1] == "설비2"


def test_get_column_values():
    """Test getting column values"""
    df = pl.DataFrame({
        "Issue": ["Issue 1", "Issue 2", None],
        "Description": ["Desc 1", "Desc 2", "Desc 3"]
    })
    
    handler = ExcelHandler()
    values = handler.get_column_values(df, "Issue")
    
    assert len(values) == 3
    assert values[0] == "Issue 1"
    assert values[2] is None


def test_is_empty_value():
    """Test checking empty values"""
    handler = ExcelHandler()
    
    assert handler.is_empty_value(None) is True
    assert handler.is_empty_value("") is True
    assert handler.is_empty_value("  ") is True
    assert handler.is_empty_value("value") is False
    assert handler.is_empty_value(0) is False


def test_write_excel():
    """Test writing Excel file"""
    df = pl.DataFrame({
        "Issue": ["Issue 1", "Issue 2"],
        "불량명": ["불량A", "불량B"]
    })
    
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        handler = ExcelHandler()
        result_path = handler.write_excel(df, tmp_path, "TestSheet")
        
        assert Path(result_path).exists()
        
        # Read back and verify
        read_df = handler.read_excel(result_path, "TestSheet")
        assert len(read_df) == 2
        assert "불량명" in read_df.columns
    finally:
        Path(tmp_path).unlink(missing_ok=True)
