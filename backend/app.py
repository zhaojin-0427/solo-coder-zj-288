from flask import Flask
from flask_cors import CORS
import os
from extensions import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wedding.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'wedding-bridesmaid-secret-key'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

from routes.wedding import wedding_bp
from routes.task import task_bp
from routes.bridesmaid import bridesmaid_bp
from routes.timeline import timeline_bp
from routes.emergency import emergency_bp
from routes.stats import stats_bp

app.register_blueprint(wedding_bp, url_prefix='/api/wedding')
app.register_blueprint(task_bp, url_prefix='/api/tasks')
app.register_blueprint(bridesmaid_bp, url_prefix='/api/bridesmaids')
app.register_blueprint(timeline_bp, url_prefix='/api/timeline')
app.register_blueprint(emergency_bp, url_prefix='/api/emergency')
app.register_blueprint(stats_bp, url_prefix='/api/stats')

@app.route('/api/health')
def health_check():
    return {'status': 'ok', 'message': 'Wedding coordination system is running'}

if __name__ == '__main__':
    with app.app_context():
        from models import Wedding, Bridesmaid, Task, TaskAdjustment, TimelineNode, TimelineAssignment, EmergencyContact
        db.create_all()
        from seed_data import seed_database
        seed_database()
    app.run(host='0.0.0.0', port=9702, debug=True)
