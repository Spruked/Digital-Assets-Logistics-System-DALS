#!/usr/bin/env python3
"""
DALS Minting Plugins
Alpha CertSig and TrueMark minting modules
"""

# Plugin exports
__all__ = [
    'AlphaCertSigMinter',
    'TrueMarkMinter',
    'mint_alpha_certificate',
    'verify_alpha_certificate',
    'mint_truemark_asset',
    'verify_truemark_asset',
    'start_live_mint_session'
]

# Lazy imports for plugin loading
def __getattr__(name):
    if name == 'AlphaCertSigMinter':
        from .alpha_certsig import AlphaCertSigMinter
        return AlphaCertSigMinter
    elif name == 'TrueMarkMinter':
        from .truemark import TrueMarkMinter
        return TrueMarkMinter
    elif name in ['mint_alpha_certificate', 'verify_alpha_certificate']:
        from . import alpha_certsig as acs
        return getattr(acs, name)
    elif name in ['mint_truemark_asset', 'verify_truemark_asset', 'start_live_mint_session']:
        from . import truemark as tm
        return getattr(tm, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")