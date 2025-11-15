#!/usr/bin/env python3
"""
Knowledge Immortality Engine - Demonstration Script
Complete end-to-end knowledge preservation pipeline
"""

import sys
import os
from pathlib import Path

# Add knowledge package to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

from knowledge.nft_builder import KnowledgeNFTBuilder

def demonstrate_interactive_mode():
    """Demonstrate interactive knowledge preservation"""
    print("🎭 INTERACTIVE MODE DEMONSTRATION")
    print("=" * 50)
    print("This would normally prompt for user input.")
    print("For automated demo, see demonstrate_automated_mode()")
    print()

def demonstrate_automated_mode():
    """Demonstrate automated knowledge preservation"""
    print("🤖 AUTOMATED MODE DEMONSTRATION")
    print("=" * 50)

    # Initialize the Knowledge Immortality Engine
    builder = KnowledgeNFTBuilder()

    # Sample expert data (Software Engineer)
    sample_answers = [
        "Sarah Chen",  # Name
        "React, TypeScript, Node.js, AWS",  # Stack
        "Scaled a React app from 10k to 1M daily users",  # Scaling achievement
        "Domain-Driven Design",  # Favorite pattern
        "Never deploy on Friday - always test in production",  # Biggest mistake
        "Code reviews catch 80% of bugs before they ship",  # Teaching principle
        "React, TypeScript, Python, Docker, Kubernetes",  # Mastered technologies
        "8 years",  # Experience
        "Event-driven microservices with CQRS pattern"  # Complex architecture
    ]

    print("🧠 Processing expert knowledge...")
    print("👤 Expert: Sarah Chen (Senior Software Engineer)")
    print("📊 Technologies: React, TypeScript, Node.js, AWS")
    print("⏰ Experience: 8 years")
    print()

    try:
        # Run the complete pipeline
        result = builder.run_automated("software_engineer", sample_answers)

        # Display results
        payload = result["payload"]
        ipfs = result["ipfs"]
        metadata = result["metadata"]

        print("✅ KNOWLEDGE IMMORTALIZED!")
        print("-" * 30)
        print(f"🏆 Expertise Level: {payload['expertise_level']}")
        print(f"📅 Years Experience: {payload['years_experience']}")
        print(f"🛠️  Specialties: {', '.join(payload['specialties'][:3])}")
        print(f"📚 Procedures Mastered: {len(payload['procedures_mastered'])}")
        print(f"🎓 Teaching Notes: {len(payload['teaching_notes'])}")
        print()

        print("🌐 IPFS STORAGE")
        print("-" * 30)
        print(f"📦 CID: {ipfs.get('cid', 'Generated in simulation')}")
        print(f"🔗 Gateway: {ipfs.get('gateway_url', 'ipfs.io/ipfs/...')}")
        print(f"🔐 Merkle Root: {ipfs.get('merkle_root', 'SHA-256 hash')[:16]}...")
        print()

        print("🎨 NFT METADATA")
        print("-" * 30)
        print(f"📜 Name: {metadata['name']}")
        print(f"📝 Description: {metadata['description'][:100]}...")
        print(f"🏷️  Attributes: {len(metadata['attributes'])} traits")
        print(f"🎯 Properties: IPFS CID, Merkle root, timestamps")
        print()

        print("📜 CERTIFICATE")
        print("-" * 30)
        print(f"🎨 Generated: {result['certificate']}")
        print("   Includes QR code linking to IPFS content")
        print("   Blockchain-ready for NFT minting")
        print()

        print("💾 FILES SAVED")
        print("-" * 30)
        saved_files = builder.save_result(result, "knowledge/demo_output")
        for file_type, path in saved_files.items():
            print(f"   {file_type.upper()}: {path}")
        print()

        print("🚀 READY FOR BLOCKCHAIN")
        print("-" * 30)
        print("✅ Payload validated and structured")
        print("✅ IPFS packaging complete")
        print("✅ ERC-721 metadata generated")
        print("✅ Visual certificate created")
        print("🎯 Ready to mint as immortal NFT!")
        print()

        return True

    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_supported_professions():
    """Show all supported professions"""
    print("🏥 SUPPORTED PROFESSIONS")
    print("=" * 50)

    builder = KnowledgeNFTBuilder()
    professions = builder.get_supported_professions()

    profession_examples = {
        "mechanic": "Automotive repair, diagnostics, specialized systems",
        "nurse": "Medical procedures, patient care, emergency response",
        "software_engineer": "Programming, frameworks, architecture design",
        "chef": "Culinary techniques, ingredient knowledge, plating",
        "electrician": "Electrical systems, safety protocols, troubleshooting",
        "plumber": "Plumbing systems, repair techniques, code compliance",
        "teacher": "Educational methods, subject expertise, classroom management",
        "farmer": "Agricultural practices, crop management, equipment operation",
        "welder": "Welding processes, safety standards, material knowledge"
    }

    for i, prof in enumerate(professions, 1):
        description = profession_examples.get(prof, "Professional expertise preservation")
        print("2d")
    print()

def main():
    """Main demonstration"""
    print("🧬 KNOWLEDGE IMMORTALITY ENGINE")
    print("   Preserving Human Expertise as Eternal NFTs")
    print("=" * 60)
    print()

    # Show supported professions
    show_supported_professions()

    # Demonstrate automated mode
    success = demonstrate_automated_mode()

    # Show interactive mode info
    demonstrate_interactive_mode()

    if success:
        print("🎉 DEMONSTRATION COMPLETE")
        print("   The Knowledge Immortality Engine is ready to preserve humanity's expertise!")
        print()
        print("💡 Next Steps:")
        print("   1. Set up IPFS node for production use")
        print("   2. Configure Ethereum wallet for NFT minting")
        print("   3. Start preserving expertise that matters to humanity")
        print()
        print("✨ \"Knowledge, once captured, should never be lost to time.\"")
        return 0
    else:
        print("❌ Demonstration failed")
        return 1

if __name__ == "__main__":
    exit(main())