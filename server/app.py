from backend.app import app

def main():
    """Deployment bridge for OpenEnv compliance."""
    app.run(host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
