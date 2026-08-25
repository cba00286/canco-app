#!/usr/bin/env bash
# Installs the official Nous Research Hermes Agent on THIS machine, and
# optionally points it at a local Ollama model so it runs without any
# cloud API key.
#
# Run this on your own local/persistent machine — Hermes Agent is designed
# to run continuously with filesystem/shell access, messaging gateways,
# and cron jobs, which don't fit a disposable cloud sandbox.
#
# Usage:
#   ./setup-local.sh                  # install only, keep default provider
#   ./setup-local.sh <ollama-model>   # install + configure a local Ollama model
#
# Example:
#   ./setup-local.sh llama3.1
set -euo pipefail

echo "Installing Hermes Agent (Nous Research)..."
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

if [ "${1:-}" != "" ]; then
  MODEL="$1"
  echo "Configuring Hermes Agent to use local Ollama model: ${MODEL}"
  echo "(Ollama must already be running: 'ollama serve', with the model pulled: 'ollama pull ${MODEL}')"
  hermes config set model.provider custom
  hermes config set model.base_url http://127.0.0.1:11434/v1
  hermes config set model.name "${MODEL}"
fi

echo "Done. Run 'hermes' to start, or 'hermes doctor' to check the setup."
