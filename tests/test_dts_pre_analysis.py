import pytest
from core.dts_parser import parse_dts_nodes, get_modified_nodes
from core.comparator import Comparator
from models.file_models import FileBundle, DiffSummary
from models.conflict_models import CandidateType

def test_parse_dts_nodes():
    dts_content = """
    /* Comment at top */
    / {
        model = "Demo Board";
    };
    
    // Inline comment
    &i2c1 {
        status = "okay";
        temperature@48 {
            compatible = "ti,tmp102";
            reg = <0x48>;
        };
    };
    
    &spi1 { status = "disabled"; };
    """
    
    nodes = parse_dts_nodes(dts_content)
    assert "/" in nodes
    assert "&i2c1" in nodes
    assert "&i2c1/temperature@48" in nodes
    assert "&spi1" in nodes
    
    assert nodes["/"] == ["model = \"Demo Board\""]
    assert "status = \"okay\"" in nodes["&i2c1"]
    assert "compatible = \"ti,tmp102\"" in nodes["&i2c1/temperature@48"]
    assert nodes["&spi1"] == ["status = \"disabled\""]

def test_get_modified_nodes():
    base = {
        "&i2c1": ["status = \"disabled\""],
        "&spi1": ["status = \"disabled\""]
    }
    
    vendor = {
        "&i2c1": ["status = \"disabled\""],
        "&spi1": ["status = \"okay\""] # Modified
    }
    
    customer = {
        "&i2c1": ["status = \"disabled\"", "eeprom@50 { reg = <0x50>; }"], # Modified/Added
        "&spi1": ["status = \"disabled\""]
    }
    
    vendor_mod = get_modified_nodes(base, vendor)
    customer_mod = get_modified_nodes(base, customer)
    
    assert vendor_mod == {"&spi1"}
    assert customer_mod == {"&i2c1"}
    assert not vendor_mod.intersection(customer_mod)

def test_comparator_disjoint_dts():
    # Disjoint changes should be AUTO_MERGE
    bundle = FileBundle(
        filename="test_board.dts",
        relative_path="test_board.dts",
        base_content="&i2c1 { status = \"disabled\"; };\n&spi1 { status = \"disabled\"; };",
        vendor_content="&i2c1 { status = \"disabled\"; };\n&spi1 { status = \"okay\"; };", # Vendor changes spi1
        customer_content="&i2c1 { status = \"okay\"; };\n&spi1 { status = \"disabled\"; };" # Customer changes i2c1
    )
    
    diff = DiffSummary(
        filename="test_board.dts",
        relative_path="test_board.dts",
        vendor_diff="",
        customer_diff="",
        vendor_additions=1,
        vendor_deletions=1,
        customer_additions=1,
        customer_deletions=1,
        vendor_changes=[],
        customer_changes=[]
    )
    
    comparator = Comparator()
    candidate = comparator.compare(diff, bundle)
    assert candidate.candidate_type == CandidateType.AUTO_MERGE

def test_comparator_overlapping_dts():
    # Overlapping changes should be AI_REVIEW
    bundle = FileBundle(
        filename="test_board.dts",
        relative_path="test_board.dts",
        base_content="&i2c1 { status = \"disabled\"; };",
        vendor_content="&i2c1 { status = \"okay\"; };", # Vendor changes status
        customer_content="&i2c1 { status = \"disabled\"; temperature@48 { reg = <0x48>; }; };" # Customer changes i2c1
    )
    
    diff = DiffSummary(
        filename="test_board.dts",
        relative_path="test_board.dts",
        vendor_diff="",
        customer_diff="",
        vendor_additions=1,
        vendor_deletions=1,
        customer_additions=1,
        customer_deletions=1,
        vendor_changes=[],
        customer_changes=[]
    )
    
    comparator = Comparator()
    candidate = comparator.compare(diff, bundle)
    assert candidate.candidate_type == CandidateType.AI_REVIEW
