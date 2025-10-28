# PGP Web Application

A secure, production-ready Flask web application for PGP (Pretty Good Privacy) encryption and decryption of files. Built with modern web technologies and containerized with Docker for easy deployment.

## Features

### 🔐 Core PGP Functionality
- **File Encryption**: Upload and encrypt files for multiple recipients
- **File Decryption**: Decrypt PGP-encrypted files with your private key
- **Key Management**: Generate, import, export, and manage PGP keys
- **Key Generation**: Create new PGP key pairs with customizable settings

### 🎨 Modern User Interface
- **Beautiful UI**: Bootstrap 5-powered responsive design
- **Drag & Drop**: Intuitive file upload with drag-and-drop support
- **Real-time Feedback**: Progress indicators and status updates
- **Mobile Friendly**: Works seamlessly on desktop and mobile devices

### 🛡️ Security Features
- **Local Processing**: All encryption/decryption happens locally
- **No Cloud Storage**: Files are processed and deleted after operations
- **CSRF Protection**: Built-in protection against cross-site request forgery
- **Input Validation**: Comprehensive validation and sanitization

### 🚀 Production Ready
- **Docker Support**: Complete containerization with Docker and docker-compose
- **Nginx Integration**: Reverse proxy configuration for production
- **Health Checks**: Built-in health monitoring endpoints
- **Logging**: Comprehensive logging for monitoring and debugging

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd pgp-web-app
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

### Development Setup

1. **Prerequisites**
   - Python 3.11+
   - GnuPG installed on your system

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## Usage Guide

### 1. Generate PGP Key Pair
- Navigate to "Generate Key" from the main menu
- Enter your name and email address
- Choose key length (2048, 3072, or 4096 bits)
- Optionally set a passphrase for extra security
- Click "Generate Key Pair"

### 2. Encrypt Files
- Go to the "Encrypt" page
- Upload a file (drag & drop or click to browse)
- Select one or more recipients from your public keys
- Click "Encrypt File"
- Download the encrypted file

### 3. Decrypt Files
- Go to the "Decrypt" page
- Upload an encrypted file (.gpg, .asc, .pgp)
- Enter your private key passphrase (if required)
- Click "Decrypt File"
- Download the decrypted file

### 4. Manage Keys
- Visit the "Keys" page to view all your keys
- Import public keys from others
- Export your public key to share
- View detailed key information
- Delete unwanted keys

## API Endpoints

The application provides RESTful API endpoints:

- `GET /api/health` - Health check endpoint
- `POST /api/validate-key` - Validate PGP key format
- `GET /api/key-info/<keyid>` - Get detailed key information

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Flask environment (development/production) |
| `SECRET_KEY` | `dev-secret-key` | Flask secret key (change in production!) |
| `PORT` | `5000` | Application port |

### Docker Configuration

The application includes comprehensive Docker configuration:

- **Dockerfile**: Multi-stage build with security best practices
- **docker-compose.yml**: Complete stack with volume management
- **nginx.conf**: Production-ready reverse proxy configuration

### Production Deployment

For production deployment:

1. **Set environment variables**
   ```bash
   export SECRET_KEY="your-secure-random-secret-key"
   export FLASK_ENV=production
   ```

2. **Use production compose profile**
   ```bash
   docker-compose --profile production up -d
   ```

3. **Configure SSL** (recommended)
   - Add SSL certificates to `./ssl/` directory
   - Uncomment HTTPS server block in `nginx.conf`

## Security Considerations

### File Handling
- Files are temporarily stored during processing
- Uploaded files are automatically cleaned up
- Maximum file size limit: 16MB
- Supported formats: PDF, DOC, TXT, IMG, ZIP, etc.

### Key Management
- Private keys are stored locally in GnuPG keyring
- Passphrases are processed client-side when possible
- No sensitive data is logged or transmitted

### Network Security
- CSRF protection enabled
- Security headers configured in Nginx
- Rate limiting implemented
- Input validation and sanitization

## Troubleshooting

### Common Issues

1. **GnuPG not found**
   ```bash
   # Install GnuPG
   sudo apt-get install gnupg  # Ubuntu/Debian
   brew install gnupg          # macOS
   ```

2. **Permission denied errors**
   ```bash
   # Fix permissions for Docker volumes
   sudo chown -R $(id -u):$(id -g) uploads gnupg_home logs
   ```

3. **File upload fails**
   - Check file size (max 16MB)
   - Verify file format is supported
   - Ensure sufficient disk space

### Logs

View application logs:
```bash
# Docker
docker-compose logs -f pgp-web-app

# Local development
tail -f logs/app.log
```

## Development

### Project Structure
```
pgp-web-app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── main/               # Main blueprint
│   ├── api/                # API blueprint
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   └── templates/          # Jinja2 templates
├── uploads/                # Temporary file storage
├── gnupg_home/            # GnuPG keyring
├── logs/                  # Application logs
├── Dockerfile             # Container definition
├── docker-compose.yml     # Multi-container setup
├── nginx.conf            # Reverse proxy config
├── requirements.txt       # Python dependencies
└── app.py                # Application entry point
```

### Adding Features

1. **New routes**: Add to appropriate blueprint in `app/main/` or `app/api/`
2. **Business logic**: Implement in `app/services/`
3. **Templates**: Create in `app/templates/`
4. **Static files**: Place in `app/static/` (if needed)

### Testing

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the Docker logs for error details

---

**⚠️ Security Notice**: This application handles cryptographic operations and sensitive files. Always use HTTPS in production and follow security best practices for deployment.