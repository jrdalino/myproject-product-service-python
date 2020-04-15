from __init__ import create_app

# Call the create app method
app = create_app()

# Run the application
app.run(host="0.0.0.0", port=5000, debug=True)