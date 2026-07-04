from flask import Flask
from routes.main import main_bp
from routes.download import download_bp
from routes.torrent import torrent_bp
from routes.grabber import grabber_bp
from core.cleanup import start_cleanup_thread

app = Flask(__name__)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(download_bp)
app.register_blueprint(torrent_bp)
app.register_blueprint(grabber_bp)

# Start background cleanup loop daemon
start_cleanup_thread()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
