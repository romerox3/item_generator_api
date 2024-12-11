def register_blueprints(app):
    from .difusion import difusion_bp

    app.register_blueprint(difusion_bp, url_prefix='/api')