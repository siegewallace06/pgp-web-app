"""
API routes for AJAX operations
"""
from flask import jsonify, request
from app.services.pgp_service import PGPService

# Import bp after other imports to avoid circular import
from app.api import bp


@bp.route('/key-info/<keyid>')
def get_key_info(keyid):
    """Get detailed information about a key."""
    try:
        pgp_service = PGPService()

        # Try to find the key in both public and private keys
        public_keys = pgp_service.list_keys(secret=False)
        private_keys = pgp_service.list_keys(secret=True)

        key_info = None
        for key in public_keys + private_keys:
            if key['keyid'] == keyid or key['fingerprint'] == keyid:
                key_info = key
                break

        if key_info:
            return jsonify({
                'success': True,
                'key': key_info
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Key not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving key info: {str(e)}'
        }), 500


@bp.route('/validate-key', methods=['POST'])
def validate_key():
    """Validate key data before import."""
    try:
        key_data = request.json.get('key_data', '')

        if not key_data:
            return jsonify({
                'success': False,
                'message': 'Key data is required'
            }), 400

        # Basic validation - check if it looks like a PGP key
        if '-----BEGIN PGP' not in key_data or '-----END PGP' not in key_data:
            return jsonify({
                'success': False,
                'message': 'Invalid PGP key format'
            }), 400

        return jsonify({
            'success': True,
            'message': 'Key format appears valid'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error validating key: {str(e)}'
        }), 500


@bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'PGP Web Application'
    })
