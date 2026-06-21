import sys
import os

# Fix for running from app directory
if __name__ == '__main__':
    # When running this file directly, adjust the path
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from app import create_app, db

    app = create_app()

    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
            print(f"📁 Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()