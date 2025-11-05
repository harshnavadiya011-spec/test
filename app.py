from flask import Flask, render_template
from config import Config
from extensions import db, jwt, migrate
from auth.auth import auth_bp
from api.data import bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(bp, url_prefix="/api")

    @app.route("/index")
    def home():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")
    
    @app.route("/reset-password")
    def reset():
        return render_template("reset_password.html")

    @app.route("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

