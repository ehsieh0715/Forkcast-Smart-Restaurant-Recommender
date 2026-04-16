# run.py — main entry point
# Import the create_app factory function and db object from the app package
from app import create_app, db

# Create the Flask app instance by calling the factory function
app = create_app()

# Check if the script is being run directly (not imported as a module)
if __name__ == "__main__":
    """
    1. Run the Flask development server with debug mode enabled (for easier debugging during development)
    2. Set the host to '0.0.0.0' to make the server accessible from any IP address
    3. Set the port to 5000, which is the default port for Flask applications
    """
    app.run(debug=True, host="0.0.0.0", port=5000)
