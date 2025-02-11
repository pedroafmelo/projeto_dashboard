#!/bin/bash
PYTHON=$(echo "$(command -v python3)" || "$(command -v python)")

if [ ! -x $PYTHON ]; then
    ecgho "You must install python3"
    exit 0
fi

enable_environment () {
    if [[ "$OSTYPE" == "msys" ]]; then
        source ./.venv/Script/activate
    else
        source ./.venv.bin/activate
    fi
    pip install --upgrade pip --quiet
    pip install -r ./requirements.txt --quiet
}

if [ ! -d "./.venv" ]; then
    echo "Building python environment. Please wait..."
    $PYTHON -m .venv
    enable_environment
else
    echo "Updating pyth9on environment..."
    enable_environment
fi