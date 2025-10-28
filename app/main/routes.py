"""
Main routes for the PGP Web Application
"""
from app.main import bp
import os
import logging
from flask import render_template, request, flash, redirect, url_for, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
# Import the blueprint at the bottom to avoid circular imports
from app.services.pgp_service import PGPService
from app.utils.file_utils import save_uploaded_file, get_file_path, delete_file, format_file_size, get_file_size

logger = logging.getLogger(__name__)

# Import bp after other imports to avoid circular import


@bp.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@bp.route('/keys')
def keys():
    """Key management page."""
    pgp_service = PGPService()

    # Get both public and private keys
    public_keys = pgp_service.list_keys(secret=False)
    private_keys = pgp_service.list_keys(secret=True)

    return render_template('keys.html',
                           public_keys=public_keys,
                           private_keys=private_keys)


@bp.route('/encrypt')
def encrypt():
    """File encryption page."""
    pgp_service = PGPService()
    public_keys = pgp_service.list_keys(secret=False)

    return render_template('encrypt.html', public_keys=public_keys)


@bp.route('/decrypt')
def decrypt():
    """File decryption page."""
    return render_template('decrypt.html')


@bp.route('/generate-key', methods=['GET', 'POST'])
def generate_key():
    """Generate new PGP key pair."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        passphrase = request.form.get('passphrase')
        key_length = int(request.form.get('key_length', 2048))

        if not name or not email:
            flash('Name and email are required.', 'error')
            return redirect(url_for('main.generate_key'))

        pgp_service = PGPService()
        result = pgp_service.generate_key_pair(
            name=name,
            email=email,
            passphrase=passphrase,
            key_length=key_length
        )

        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('main.keys'))
        else:
            flash(result['message'], 'error')

    return render_template('generate_key.html')


@bp.route('/import-key', methods=['POST'])
def import_key():
    """Import a PGP key."""
    key_data = request.form.get('key_data')

    if not key_data:
        flash('Key data is required.', 'error')
        return redirect(url_for('main.keys'))

    pgp_service = PGPService()
    result = pgp_service.import_key(key_data)

    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('main.keys'))


@bp.route('/export-key/<keyid>')
def export_key(keyid):
    """Export a public key."""
    pgp_service = PGPService()
    key_data = pgp_service.export_key(keyid, secret=False)

    if key_data:
        return jsonify({
            'success': True,
            'key_data': key_data
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to export key'
        }), 400


@bp.route('/delete-key/<keyid>', methods=['POST'])
def delete_key(keyid):
    """Delete a key."""
    secret = request.form.get('secret') == 'true'

    pgp_service = PGPService()
    result = pgp_service.delete_key(keyid, secret=secret)

    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('main.keys'))


@bp.route('/upload-file', methods=['POST'])
def upload_file():
    """Upload a file for encryption/decryption."""
    logger.info("File upload request received")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request URL: {request.url}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request content type: {request.content_type}")
    logger.debug(f"Request form data keys: {list(request.form.keys())}")
    logger.debug(f"Request files keys: {list(request.files.keys())}")

    try:
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        file = request.files['file']
        logger.info(f"Processing file: {file.filename}")
        logger.debug(f"File content type: {file.content_type}")
        logger.debug(
            f"File size: {file.content_length if file.content_length else 'unknown'}")

        success, filename, message = save_uploaded_file(file)
        logger.info(
            f"File save result: success={success}, filename={filename}, message={message}")

        if success:
            file_size = get_file_size(filename)
            logger.info(
                f"File uploaded successfully: {filename}, size: {file_size} bytes")
            return jsonify({
                'success': True,
                'filename': filename,
                'size': format_file_size(file_size),
                'message': message
            })
        else:
            logger.error(f"File upload failed: {message}")
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        logger.error(f"Unexpected error in file upload: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({
            'success': False,
            'message': f'Upload failed: {str(e)}',
            'error_type': 'unexpected_error'
        }), 500


@bp.route('/encrypt-file', methods=['POST'])
def encrypt_file():
    """Encrypt a file."""
    filename = request.form.get('filename')
    recipient_keys = request.form.getlist('recipients')

    if not filename or not recipient_keys:
        return jsonify({
            'success': False,
            'message': 'Filename and recipients are required'
        }), 400

    file_path = get_file_path(filename)
    if not os.path.exists(file_path):
        return jsonify({
            'success': False,
            'message': 'File not found'
        }), 404

    pgp_service = PGPService()

    # Create output filename
    name, ext = os.path.splitext(filename)
    encrypted_filename = f"{name}_encrypted{ext}.gpg"
    encrypted_path = get_file_path(encrypted_filename)

    result = pgp_service.encrypt_file(
        file_path, recipient_keys, encrypted_path)

    if result['success']:
        # Delete original file
        delete_file(filename)

        file_size = get_file_size(encrypted_filename)
        return jsonify({
            'success': True,
            'encrypted_filename': encrypted_filename,
            'size': format_file_size(file_size),
            'message': 'File encrypted successfully'
        })
    else:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 500


@bp.route('/decrypt-file', methods=['POST'])
def decrypt_file():
    """Decrypt a file."""
    logger.info("File decryption request received")

    filename = request.form.get('filename')
    passphrase = request.form.get('passphrase')

    logger.info(f"Decrypting file: {filename}")
    logger.debug(f"Passphrase provided: {'Yes' if passphrase else 'No'}")

    if not filename:
        logger.error("No filename provided in request")
        return jsonify({
            'success': False,
            'message': 'Filename is required'
        }), 400

    file_path = get_file_path(filename)
    logger.debug(f"File path: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return jsonify({
            'success': False,
            'message': 'File not found'
        }), 404

    logger.info("Initializing PGP service for decryption")
    pgp_service = PGPService()

    # Create output filename
    name, ext = os.path.splitext(filename)
    if name.endswith('_encrypted'):
        name = name.replace('_encrypted', '_decrypted')
    else:
        name = f"{name}_decrypted"

    # Remove .gpg extension if present
    if ext == '.gpg':
        # Try to determine original extension
        base_name, original_ext = os.path.splitext(name)
        if original_ext:
            decrypted_filename = f"{base_name}{original_ext}"
        else:
            decrypted_filename = f"{name}.txt"
    else:
        decrypted_filename = f"{name}{ext}"

    decrypted_path = get_file_path(decrypted_filename)
    logger.info(f"Output file will be: {decrypted_filename}")
    logger.debug(f"Output path: {decrypted_path}")

    logger.info("Starting file decryption process")
    result = pgp_service.decrypt_file(file_path, passphrase, decrypted_path)
    logger.info(f"Decryption result: {result}")

    if result['success']:
        logger.info("File decrypted successfully, deleting encrypted file")
        # Delete encrypted file
        delete_file(filename)

        file_size = get_file_size(decrypted_filename)
        logger.info(
            f"Decryption complete: {decrypted_filename}, size: {file_size} bytes")
        return jsonify({
            'success': True,
            'decrypted_filename': decrypted_filename,
            'size': format_file_size(file_size),
            'message': 'File decrypted successfully'
        })
    else:
        logger.error(f"File decryption failed: {result['message']}")
        return jsonify({
            'success': False,
            'message': result['message']
        }), 500


@bp.route('/download-file/<filename>')
def download_file(filename):
    """Download a file."""
    try:
        file_path = get_file_path(filename)
        if not os.path.exists(file_path):
            flash('File not found.', 'error')
            return redirect(url_for('main.index'))

        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@bp.route('/delete-file/<filename>', methods=['POST'])
def delete_uploaded_file(filename):
    """Delete an uploaded file."""
    if delete_file(filename):
        return jsonify({'success': True, 'message': 'File deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to delete file'}), 500
