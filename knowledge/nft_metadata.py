# knowledge/nft_metadata.py
import qrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class NFTMetadataBuilder:
    """
    NFT Metadata Builder
    Creates ERC-721 compatible metadata and visual certificates
    Phase 11-A2: Knowledge Preservation Pipeline
    """

    def __init__(self, template_path: str = None):
        self.template_path = template_path or "knowledge/templates/certificate_template.png"
        self.fonts = self._load_fonts()

    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load fonts for certificate generation"""
        fonts = {}

        # Try to load system fonts, fallback to default
        try:
            fonts['title'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            fonts['subtitle'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            fonts['body'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            fonts['small'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except OSError:
            # Fallback to default font
            try:
                fonts['title'] = ImageFont.truetype("arial.ttf", 80)
                fonts['subtitle'] = ImageFont.truetype("arial.ttf", 40)
                fonts['body'] = ImageFont.truetype("arial.ttf", 32)
                fonts['small'] = ImageFont.truetype("arial.ttf", 24)
            except OSError:
                # Ultimate fallback
                fonts['title'] = ImageFont.load_default()
                fonts['subtitle'] = ImageFont.load_default()
                fonts['body'] = ImageFont.load_default()
                fonts['small'] = ImageFont.load_default()

        return fonts

    def build_metadata(self, payload: Dict[str, Any], ipfs_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build ERC-721 compatible NFT metadata
        """
        logger.info(f"Building NFT metadata for {payload.get('expertise_level', 'Unknown')}")

        # Base metadata structure
        metadata = {
            "name": f"{payload['expertise_level']} Expertise Knowledge NFT",
            "description": self._generate_description(payload),
            "image": ipfs_data.get("gateway_url", ipfs_data.get("ipfs_url", "")),
            "external_url": ipfs_data.get("gateway_url", ""),
            "animation_url": None,  # Could add video certificates later
            "attributes": self._build_attributes(payload, ipfs_data),
            "properties": {
                "content_hash": ipfs_data.get("content_hash", ""),
                "merkle_root": ipfs_data.get("merkle_root", ""),
                "ipfs_cid": ipfs_data.get("cid", ""),
                "filecoin_ready": ipfs_data.get("filecoin_ready", False),
                "knowledge_payload": payload,
                "packaging_metadata": {
                    "packaged_at": ipfs_data.get("packaging_timestamp"),
                    "packager_version": "NFTMetadataBuilder v1.0"
                }
            }
        }

        # Add founder seal and verification
        metadata.update({
            "founder_seal": "TrueMark Certified - Alpha CertSig",
            "verification": {
                "issuer": "Digital Asset Logistics System (DALS)",
                "standard": "Knowledge NFT v1.0",
                "blockchain": "Ethereum ERC-721",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        })

        return metadata

    def _generate_description(self, payload: Dict[str, Any]) -> str:
        """Generate compelling NFT description"""
        profession = payload.get('profession', 'Professional').title()
        years = payload.get('years_experience', 0)
        specialties = payload.get('specialties', [])
        procedures = payload.get('procedures_mastered', [])

        description_parts = [
            f"Preserved expertise of a {years}+ year veteran {profession}.",
            f"Master of {len(specialties)} specialties and {len(procedures)} advanced procedures."
        ]

        if specialties:
            top_specialties = specialties[:3]
            description_parts.append(f"Specializes in: {', '.join(top_specialties)}.")

        if payload.get('teaching_notes'):
            description_parts.append("Includes wisdom and lessons for future generations.")

        description_parts.extend([
            "Verified by Alpha CertSig.",
            "Knowledge immortality achieved through blockchain.",
            "One of a kind digital legacy preservation."
        ])

        return " ".join(description_parts)

    def _build_attributes(self, payload: Dict[str, Any], ipfs_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build OpenSea-compatible attributes"""
        attributes = []

        # Core attributes
        attributes.extend([
            {
                "trait_type": "Profession",
                "value": payload.get('profession', 'Unknown').title(),
                "display_type": None
            },
            {
                "trait_type": "Specialization",
                "value": payload.get('specialization') or payload.get('profession', 'General').title(),
                "display_type": None
            },
            {
                "trait_type": "Years Experience",
                "value": payload.get('years_experience', 0),
                "display_type": "number"
            },
            {
                "trait_type": "Expertise Tier",
                "value": self._calculate_expertise_tier(payload),
                "display_type": None
            }
        ])

        # Numeric attributes
        attributes.extend([
            {
                "trait_type": "Specialties Count",
                "value": len(payload.get('specialties', [])),
                "display_type": "number"
            },
            {
                "trait_type": "Procedures Mastered",
                "value": len(payload.get('procedures_mastered', [])),
                "display_type": "number"
            },
            {
                "trait_type": "Teaching Points",
                "value": len(payload.get('teaching_notes', [])),
                "display_type": "number"
            },
            {
                "trait_type": "Knowledge Density",
                "value": payload.get('knowledge_density_score', 0),
                "display_type": "number",
                "max_value": 100
            }
        ])

        # Specialty tags (limit to 5 for readability)
        for i, specialty in enumerate(payload.get('specialties', [])[:5]):
            attributes.append({
                "trait_type": f"Specialty {i+1}",
                "value": specialty[:30],  # Truncate long names
                "display_type": None
            })

        # Verification attributes
        attributes.extend([
            {
                "trait_type": "Verified",
                "value": "Alpha CertSig",
                "display_type": None
            },
            {
                "trait_type": "Merkle Root",
                "value": ipfs_data.get('merkle_root', '')[:16] + "...",
                "display_type": None
            },
            {
                "trait_type": "Filecoin Ready",
                "value": "Yes" if ipfs_data.get('filecoin_ready') else "No",
                "display_type": None
            }
        ])

        return attributes

    def _calculate_expertise_tier(self, payload: Dict[str, Any]) -> str:
        """Calculate expertise tier based on experience and knowledge"""
        years = payload.get('years_experience', 0)
        knowledge_score = payload.get('knowledge_density_score', 0)

        # Tier calculation logic
        if years >= 20 and knowledge_score >= 80:
            return "Grand Master"
        elif years >= 15 and knowledge_score >= 60:
            return "Master"
        elif years >= 10 and knowledge_score >= 40:
            return "Expert"
        elif years >= 5 and knowledge_score >= 20:
            return "Advanced"
        elif years >= 2:
            return "Intermediate"
        else:
            return "Apprentice"

    def generate_certificate(self, payload: Dict[str, Any], ipfs_data: Dict[str, Any],
                           output_path: str, width: int = 1200, height: int = 1600) -> str:
        """
        Generate visual certificate with QR code
        """
        logger.info(f"Generating certificate for {payload.get('expertise_level', 'Unknown')}")

        # Create base image
        img = Image.new('RGB', (width, height), color='#0a0a0a')
        draw = ImageDraw.Draw(img)

        # Colors
        colors = {
            'title': '#00ff88',
            'subtitle': '#ffffff',
            'body': '#cccccc',
            'accent': '#00ff88',
            'qr': '#ffffff'
        }

        # Layout constants
        margin = 80
        y_pos = margin

        # Title
        title_text = "KNOWLEDGE NFT CERTIFICATE"
        draw.text((width//2, y_pos), title_text, fill=colors['title'],
                 font=self.fonts['title'], anchor="mm")
        y_pos += 120

        # Expertise level
        expertise = payload.get('expertise_level', 'Professional Expert')
        draw.text((width//2, y_pos), expertise, fill=colors['subtitle'],
                 font=self.fonts['subtitle'], anchor="mm")
        y_pos += 80

        # Years experience
        years = payload.get('years_experience', 0)
        if years > 0:
            years_text = f"{years} Years of Experience"
            draw.text((width//2, y_pos), years_text, fill=colors['body'],
                     font=self.fonts['body'], anchor="mm")
            y_pos += 60

        # Specialties section
        y_pos += 40
        specialties = payload.get('specialties', [])[:5]  # Limit to 5
        if specialties:
            draw.text((margin, y_pos), "AREAS OF MASTERY:", fill=colors['accent'],
                     font=self.fonts['body'])
            y_pos += 50

            for specialty in specialties:
                wrapped = textwrap.wrap(specialty, width=50)
                for line in wrapped:
                    draw.text((margin + 20, y_pos), f"• {line}", fill=colors['body'],
                             font=self.fonts['body'])
                    y_pos += 40
                y_pos += 10

        # Teaching insights
        y_pos += 30
        teaching = payload.get('teaching_notes', [])[:3]  # Limit to 3
        if teaching:
            draw.text((margin, y_pos), "WISDOM FOR FUTURE GENERATIONS:", fill=colors['accent'],
                     font=self.fonts['body'])
            y_pos += 50

            for insight in teaching:
                wrapped = textwrap.wrap(insight, width=55)
                for line in wrapped:
                    draw.text((margin + 20, y_pos), f"• {line}", fill=colors['body'],
                             font=self.fonts['body'])
                    y_pos += 35
                y_pos += 15

        # QR Code section
        qr_size = 300
        qr_x = width - margin - qr_size
        qr_y = height - margin - qr_size - 100

        # Generate QR code
        qr_url = ipfs_data.get('gateway_url', ipfs_data.get('ipfs_url', 'https://alpha-certsig.com'))
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color=colors['qr'], back_color='#0a0a0a')
        qr_img = qr_img.resize((qr_size, qr_size))
        img.paste(qr_img, (qr_x, qr_y))

        # QR label
        draw.text((qr_x + qr_size//2, qr_y + qr_size + 20), "SCAN TO VERIFY",
                 fill=colors['accent'], font=self.fonts['small'], anchor="mm")

        # Footer
        footer_y = height - margin
        footer_text = "Alpha CertSig • TrueMark Certified • Knowledge Immortalized"
        draw.text((width//2, footer_y), footer_text, fill=colors['accent'],
                 font=self.fonts['small'], anchor="mm")

        # Save certificate
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path_obj)

        logger.info(f"Certificate generated: {output_path}")
        return str(output_path_obj)

    def create_preview_image(self, payload: Dict[str, Any], ipfs_data: Dict[str, Any],
                           output_path: str) -> str:
        """Create a smaller preview image for NFT marketplaces"""
        return self.generate_certificate(payload, ipfs_data, output_path,
                                       width=600, height=800)

    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate NFT metadata for marketplace compatibility"""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "opensea_compatible": True
        }

        # Required fields
        required = ["name", "description", "image"]
        for field in required:
            if not metadata.get(field):
                validation["errors"].append(f"Missing required field: {field}")
                validation["valid"] = False

        # Image URL validation
        image_url = metadata.get("image", "")
        if image_url and not (image_url.startswith("ipfs://") or image_url.startswith("https://")):
            validation["warnings"].append("Image URL should be IPFS or HTTPS")

        # Attributes validation
        attributes = metadata.get("attributes", [])
        if not isinstance(attributes, list):
            validation["errors"].append("Attributes must be a list")
            validation["valid"] = False
        else:
            for i, attr in enumerate(attributes):
                if not isinstance(attr, dict):
                    validation["errors"].append(f"Attribute {i} must be a dict")
                    validation["valid"] = False
                elif "trait_type" not in attr or "value" not in attr:
                    validation["warnings"].append(f"Attribute {i} missing trait_type or value")

        return validation