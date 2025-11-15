# knowledge/nft_builder.py
from .interview_engine import KnowledgeInterviewEngine
from .structurer import KnowledgeStructurer
from .ipfs_packager import IPFSPackager
from .nft_metadata import NFTMetadataBuilder
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class KnowledgeNFTBuilder:
    """
    Full Knowledge Immortality Pipeline Orchestrator
    Phase 11-A2: Complete end-to-end knowledge preservation system
    """

    def __init__(self, ipfs_host: str = "localhost", ipfs_port: int = 5001):
        self.interview_engine = KnowledgeInterviewEngine()
        self.structurer = KnowledgeStructurer()
        self.ipfs_packager = IPFSPackager(ipfs_host, ipfs_port)
        self.nft_builder = NFTMetadataBuilder()

        # Pipeline state
        self.pipeline_state = {
            "stage": "initialized",
            "progress": 0,
            "start_time": None,
            "end_time": None,
            "errors": [],
            "warnings": []
        }

    def run_interactive(self, profession: str, specialization: str = None,
                       assets: List[Path] = None) -> Dict[str, Any]:
        """
        Run the complete interactive knowledge preservation pipeline
        """
        self._reset_pipeline()
        self.pipeline_state["start_time"] = datetime.utcnow().isoformat() + "Z"

        try:
            # Stage 1: Interview
            self._update_progress(10, "Starting interview session")
            session_info = self.interview_engine.start_session(profession, specialization)
            print(f"\n🧠 KNOWLEDGE IMMORTALITY ENGINE ACTIVATED")
            print(f"📋 Interview Session: {session_info['session_id']}")
            print(f"❓ Questions to Answer: {session_info['question_count']}")
            print(f"⏱️  Estimated Time: {session_info['estimated_time']}\n")

            # Interactive Q&A
            questions = session_info["questions"]
            for i, question in enumerate(questions):
                print(f"Q{i+1}/{len(questions)}: {question}")
                answer = input("> ").strip()
                if answer:
                    result = self.interview_engine.submit_answer(i, answer)
                    progress = result["remaining_questions"]
                    print(f"✅ Answer recorded. {progress} questions remaining.\n")
                else:
                    print("⚠️  Skipping question (can be edited later)\n")

            self._update_progress(40, "Interview completed")

            # Stage 2: Structure knowledge
            self._update_progress(50, "Structuring knowledge payload")
            raw_data = self.interview_engine.get_raw_data()
            payload = self.structurer.build_nft_payload(raw_data)

            # Enhance payload
            payload = self.structurer.enhance_payload(payload)

            # Validate payload
            validation = self.structurer.validate_payload(payload)
            if not validation["valid"]:
                print("⚠️  Payload validation issues:")
                for error in validation["errors"]:
                    print(f"   ❌ {error}")
                if input("Continue anyway? (y/N): ").lower() != 'y':
                    raise ValueError("Payload validation failed")

            self._update_progress(70, "Knowledge structured and validated")

            # Stage 3: IPFS packaging
            self._update_progress(80, "Packaging for IPFS storage")
            ipfs_result = self.ipfs_packager.package(payload, assets)

            self._update_progress(90, "IPFS packaging complete")

            # Stage 4: NFT metadata and certificate
            self._update_progress(95, "Generating NFT metadata and certificate")
            nft_metadata = self.nft_builder.build_metadata(payload, ipfs_result)

            # Generate certificate
            cert_path = f"knowledge/certificates/cert_{int(time.time())}.png"
            cert_path = self.nft_builder.generate_certificate(payload, ipfs_result, cert_path)

            # Validate metadata
            metadata_validation = self.nft_builder.validate_metadata(nft_metadata)
            if not metadata_validation["valid"]:
                print("⚠️  Metadata validation issues:")
                for error in metadata_validation["errors"]:
                    print(f"   ❌ {error}")

            self._update_progress(100, "NFT creation complete")

            # Final result
            result = {
                "success": True,
                "session_id": session_info["session_id"],
                "payload": payload,
                "ipfs": ipfs_result,
                "metadata": nft_metadata,
                "certificate": cert_path,
                "ready_to_mint": True,
                "pipeline_stats": self.pipeline_state.copy(),
                "validation": {
                    "payload": validation,
                    "metadata": metadata_validation
                }
            }

            self._print_success_summary(result)
            return result

        except Exception as e:
            self.pipeline_state["errors"].append(str(e))
            self.pipeline_state["stage"] = "failed"
            logger.error(f"Pipeline failed: {e}")
            raise

        finally:
            self.pipeline_state["end_time"] = datetime.utcnow().isoformat() + "Z"

    def run_automated(self, profession: str, answers: List[str],
                     specialization: str = None, assets: List[Path] = None) -> Dict[str, Any]:
        """
        Run the pipeline with pre-provided answers (for batch processing)
        """
        self._reset_pipeline()
        self.pipeline_state["start_time"] = datetime.utcnow().isoformat() + "Z"

        try:
            # Start session
            session_info = self.interview_engine.start_session(profession, specialization)

            # Submit all answers
            for i, answer in enumerate(answers):
                if i < len(session_info["questions"]):
                    self.interview_engine.submit_answer(i, answer)

            # Run remaining pipeline (same as interactive)
            raw_data = self.interview_engine.get_raw_data()
            payload = self.structurer.build_nft_payload(raw_data)
            payload = self.structurer.enhance_payload(payload)

            ipfs_result = self.ipfs_packager.package(payload, assets)
            nft_metadata = self.nft_builder.build_metadata(payload, ipfs_result)

            cert_path = f"knowledge/certificates/cert_{int(time.time())}_auto.png"
            cert_path = self.nft_builder.generate_certificate(payload, ipfs_result, cert_path)

            result = {
                "success": True,
                "session_id": session_info["session_id"],
                "payload": payload,
                "ipfs": ipfs_result,
                "metadata": nft_metadata,
                "certificate": cert_path,
                "ready_to_mint": True,
                "pipeline_stats": self.pipeline_state.copy()
            }

            return result

        except Exception as e:
            self.pipeline_state["errors"].append(str(e))
            raise

        finally:
            self.pipeline_state["end_time"] = datetime.utcnow().isoformat() + "Z"

    def save_result(self, result: Dict[str, Any], output_dir: str = "knowledge/output") -> Dict[str, str]:
        """Save all pipeline outputs to files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        session_id = result["session_id"]
        saved_files = {}

        # Save payload
        payload_file = output_dir / f"{session_id}_payload.json"
        with open(payload_file, 'w', encoding='utf-8') as f:
            json.dump(result["payload"], f, indent=2, ensure_ascii=False)
        saved_files["payload"] = str(payload_file)

        # Save metadata
        metadata_file = output_dir / f"{session_id}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(result["metadata"], f, indent=2, ensure_ascii=False)
        saved_files["metadata"] = str(metadata_file)

        # Save IPFS info
        ipfs_file = output_dir / f"{session_id}_ipfs.json"
        with open(ipfs_file, 'w', encoding='utf-8') as f:
            json.dump(result["ipfs"], f, indent=2, ensure_ascii=False)
        saved_files["ipfs"] = str(ipfs_file)

        # Save pipeline stats
        stats_file = output_dir / f"{session_id}_pipeline.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(result["pipeline_stats"], f, indent=2, ensure_ascii=False)
        saved_files["pipeline"] = str(stats_file)

        # Certificate is already saved
        saved_files["certificate"] = result["certificate"]

        logger.info(f"Saved {len(saved_files)} files to {output_dir}")
        return saved_files

    def _reset_pipeline(self):
        """Reset pipeline state"""
        self.pipeline_state = {
            "stage": "initialized",
            "progress": 0,
            "start_time": None,
            "end_time": None,
            "errors": [],
            "warnings": []
        }

    def _update_progress(self, progress: int, stage: str):
        """Update pipeline progress"""
        self.pipeline_state["progress"] = progress
        self.pipeline_state["stage"] = stage
        logger.info(f"Pipeline progress: {progress}% - {stage}")

    def _print_success_summary(self, result: Dict[str, Any]):
        """Print success summary"""
        payload = result["payload"]
        ipfs = result["ipfs"]

        print(f"\n🎉 KNOWLEDGE IMMORTALITY ACHIEVED!")
        print(f"🏆 {payload['expertise_level']}")
        print(f"📊 {payload['years_experience']} years experience")
        print(f"🛠️  {len(payload['specialties'])} specialties mastered")
        print(f"📚 {len(payload['procedures_mastered'])} procedures mastered")
        print(f"🎓 {len(payload['teaching_notes'])} wisdom points preserved")
        print(f"🔗 IPFS CID: {ipfs.get('cid', 'N/A')}")
        print(f"🌐 Gateway: {ipfs.get('gateway_url', 'N/A')}")
        print(f"📜 Certificate: {result['certificate']}")
        print(f"💎 Ready to mint on Ethereum as ERC-721 NFT!")
        print(f"\n✨ This knowledge will live forever on the blockchain.")

    def get_supported_professions(self) -> List[str]:
        """Get list of supported professions"""
        return list(self.interview_engine.profiles.keys())

    def get_profession_templates(self, profession: str) -> Dict[str, Any]:
        """Get interview templates for a profession"""
        return self.interview_engine.profiles.get(profession, {})

    def validate_profession_support(self, profession: str, specialization: str = None) -> Dict[str, Any]:
        """Validate if a profession/specialization is supported"""
        validation = {
            "supported": False,
            "profession_found": False,
            "specialization_found": False,
            "fallback_available": False
        }

        profiles = self.interview_engine.profiles

        if profession in profiles:
            validation["profession_found"] = True
            validation["supported"] = True

            if specialization and isinstance(profiles[profession], dict):
                if specialization in profiles[profession]:
                    validation["specialization_found"] = True
                elif "General" in profiles[profession]:
                    validation["fallback_available"] = True

        return validation


# CLI Interface
def main():
    """Command-line interface for the Knowledge NFT Builder"""
    import argparse

    parser = argparse.ArgumentParser(description="Knowledge Immortality Engine - Preserve expertise as NFTs")
    parser.add_argument("profession", help="Profession to preserve (e.g., mechanic, nurse, software_engineer)")
    parser.add_argument("--specialization", help="Specific specialization (e.g., Ford, ER, React)")
    parser.add_argument("--interactive", action="store_true", help="Run interactive interview")
    parser.add_argument("--answers", nargs="*", help="Pre-provided answers for automated processing")
    parser.add_argument("--assets", nargs="*", help="Additional asset files to include")
    parser.add_argument("--output-dir", default="knowledge/output", help="Output directory")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize builder
    builder = KnowledgeNFTBuilder()

    # Validate profession support
    validation = builder.validate_profession_support(args.profession, args.specialization)
    if not validation["supported"]:
        print(f"⚠️  Profession '{args.profession}' not fully supported.")
        if validation["fallback_available"]:
            print("   Using general template.")
        else:
            print("   Available professions:", ", ".join(builder.get_supported_professions()))
            return

    try:
        # Run pipeline
        if args.interactive or not args.answers:
            result = builder.run_interactive(args.profession, args.specialization,
                                           [Path(a) for a in (args.assets or [])])
        else:
            result = builder.run_automated(args.profession, args.answers, args.specialization,
                                         [Path(a) for a in (args.assets or [])])

        # Save results
        saved_files = builder.save_result(result, args.output_dir)

        print(f"\n💾 Files saved to: {args.output_dir}")
        for file_type, path in saved_files.items():
            print(f"   {file_type}: {path}")

    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())