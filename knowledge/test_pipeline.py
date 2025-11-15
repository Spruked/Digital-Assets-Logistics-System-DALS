# knowledge/test_pipeline.py
"""
Test script for the Knowledge Immortality Engine pipeline
Validates all components work together correctly
"""

import sys
import os
from pathlib import Path
import json
import logging

# Add current directory and knowledge package to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

from knowledge.nft_builder import KnowledgeNFTBuilder

def test_basic_functionality():
    """Test basic pipeline functionality with sample data"""
    print("🧪 Testing Knowledge Immortality Engine Pipeline")

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize builder
    builder = KnowledgeNFTBuilder()

    # Test profession support
    professions = builder.get_supported_professions()
    print(f"✅ Supported professions: {len(professions)}")
    assert "software_engineer" in professions

    # Test profession validation
    validation = builder.validate_profession_support("software_engineer", "React")
    print(f"✅ Profession validation: {validation}")
    assert validation["supported"]

    # Test automated pipeline with sample answers
    sample_answers = [
        "Test Engineer",  # What is your name and current role?
        "Python, React, AWS",  # Primary stack
        "Built a system handling 1M users",  # Biggest system scaled
        "MVC pattern",  # Design pattern
        "Database connection pool exhaustion",  # Worst production fire
        "Always write tests first",  # One principle
        "Python, JavaScript, Docker",  # Languages/frameworks mastered
        "5 years",  # How many years coding professionally?
        "Microservices architecture with Kubernetes"  # Most complex system
    ]

    print("🚀 Running automated pipeline test...")
    try:
        result = builder.run_automated("software_engineer", sample_answers)

        # Validate result structure
        assert result["success"] == True
        assert "payload" in result
        assert "ipfs" in result
        assert "metadata" in result
        assert "certificate" in result
        assert result["ready_to_mint"] == True

        # Validate payload
        payload = result["payload"]
        assert payload["name"] == "Test Engineer"
        assert payload["years_experience"] == 5
        assert "Python" in payload["specialties"]
        assert len(payload["procedures_mastered"]) > 0

        # Validate metadata
        metadata = result["metadata"]
        assert metadata["name"].startswith("Software Engineer Expertise")
        assert "attributes" in metadata
        assert len(metadata["attributes"]) > 0

        # Validate IPFS (simulation mode)
        ipfs = result["ipfs"]
        assert "cid" in ipfs or "simulation_mode" in ipfs

        print("✅ Pipeline test completed successfully!")
        print(f"📊 Payload expertise level: {payload['expertise_level']}")
        print(f"🛠️  Specialties captured: {len(payload['specialties'])}")
        print(f"📚 Procedures mastered: {len(payload['procedures_mastered'])}")

        # Save test results
        test_output_dir = Path("knowledge/test_output")
        saved_files = builder.save_result(result, str(test_output_dir))
        print(f"💾 Test results saved to: {test_output_dir}")

        return True

    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interview_engine():
    """Test interview engine independently"""
    print("\n🧪 Testing Interview Engine")

    from knowledge.interview_engine import KnowledgeInterviewEngine

    engine = KnowledgeInterviewEngine()

    # Test session creation
    session = engine.start_session("mechanic")
    assert session["question_count"] > 0
    assert session["session_id"].startswith("knowledge_")

    # Test answer submission
    result = engine.submit_answer(0, "Test answer")
    assert result["accepted"] == True

    # Test raw data retrieval
    raw_data = engine.get_raw_data()
    assert len(raw_data["answers"]) > 0
    assert raw_data["profession"] == "mechanic"

    print("✅ Interview engine test passed!")
    return True

def test_structurer():
    """Test knowledge structurer independently"""
    print("\n🧪 Testing Knowledge Structurer")

    from knowledge.structurer import KnowledgeStructurer

    structurer = KnowledgeStructurer()

    # Test with sample raw data in correct format
    raw_data = {
        "profession": "software_engineer",
        "answers": [
            {"question": "What is your name?", "answer": "John Doe"},
            {"question": "How many years of experience do you have?", "answer": "10 years"},
            {"question": "What are your top specialties?", "answer": "Python, React, AWS"},
            {"question": "What procedures do you master?", "answer": "Building web applications, Microservices"},
            {"question": "What advice would you give?", "answer": "Learn testing first"}
        ]
    }

    # Test payload building
    payload = structurer.build_nft_payload(raw_data)
    assert payload["name"] == "John Doe"
    assert payload["years_experience"] == 10
    assert "Python" in payload["specialties"]

    # Test enhancement
    enhanced = structurer.enhance_payload(payload)
    assert "expertise_level" in enhanced

    # Test validation
    validation = structurer.validate_payload(enhanced)
    assert validation["valid"] == True

    print("✅ Knowledge structurer test passed!")
    return True

def test_nft_metadata():
    """Test NFT metadata builder independently"""
    print("\n🧪 Testing NFT Metadata Builder")

    from knowledge.nft_metadata import NFTMetadataBuilder

    builder = NFTMetadataBuilder()

    # Sample payload and IPFS data
    payload = {
        "name": "Test Expert",
        "profession": "software_engineer",
        "years_experience": 8,
        "specialties": ["Python", "React"],
        "expertise_level": "Senior"
    }

    ipfs_result = {
        "cid": "QmTest123",
        "gateway_url": "https://ipfs.io/ipfs/QmTest123",
        "merkle_root": "abc123"
    }

    # Test metadata building
    metadata = builder.build_metadata(payload, ipfs_result)
    assert metadata["name"] == "Senior Expertise Knowledge NFT"
    assert len(metadata["attributes"]) > 0

    # Test validation
    validation = builder.validate_metadata(metadata)
    assert validation["valid"] == True

    print("✅ NFT metadata builder test passed!")
    return True

def main():
    """Run all tests"""
    print("🚀 Knowledge Immortality Engine - Test Suite")
    print("=" * 50)

    tests = [
        ("Basic Pipeline", test_basic_functionality),
        ("Interview Engine", test_interview_engine),
        ("Knowledge Structurer", test_structurer),
        ("NFT Metadata Builder", test_nft_metadata)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Knowledge Immortality Engine is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit(main())