from backend.app import app

def main():
    """Main entry point for multi-mode deployment."""
    app.run(host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
