from flask import Flask
from flask_cors import CORS

from config import HOST, PORT, DEBUG, TEMPLATES_DIR, STATIC_DIR
from routes import register_routes

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__, 
                template_folder=str(TEMPLATES_DIR),
                static_folder=str(STATIC_DIR))
    
    # 启用CORS
    CORS(app)
    
    # 注册路由
    register_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True) 