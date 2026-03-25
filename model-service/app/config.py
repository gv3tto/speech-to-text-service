# config.py — Settings for the model service
# We keep settings separate so they're easy to change later

# Which Whisper model to use
# Options: "tiny", "base", "small", "medium", "large"
# "tiny" is best for development — fast to download (~75MB) and fast to run
# You can upgrade to "base" or "small" later for better accuracy
MODEL_NAME = "tiny"