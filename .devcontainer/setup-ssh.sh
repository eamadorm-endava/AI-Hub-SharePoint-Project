#!/bin/bash
set -euo pipefail

echo "Setting up SSH config and Git signing..."

# Define paths
SSH_DIR="$HOME/.ssh"
CONFIG_SRC="$SSH_DIR/config"
CONFIG_SAFE="$SSH_DIR/config-devcontainer"
KEY_PATH="$SSH_DIR/id_ed25519"

# 1. Copy SSH config if it exists
if [[ -f "$CONFIG_SRC" ]]; then
  cp "$CONFIG_SRC" "$CONFIG_SAFE"
  chmod 600 "$CONFIG_SAFE"
  echo "Copied SSH config to $CONFIG_SAFE"
else
  echo "SSH config not found at $CONFIG_SRC — skipping copy"
fi

# 2. Configure Git to use the safe copy if it exists
if [[ -f "$CONFIG_SAFE" ]]; then
  git config --global core.sshCommand "ssh -F $CONFIG_SAFE"
  echo "Git configured to use safe SSH config"
else
  echo "Safe SSH config not found — skipping sshCommand override"
fi

# 3. Load SSH key if it exists and is not already loaded
if [[ -f "$KEY_PATH" ]]; then
  if ssh-add -L | grep -q "$(ssh-keygen -y -f "$KEY_PATH" 2>/dev/null | head -n 1)"; then
    echo "SSH key is already loaded in agent"
  else
    ssh-add "$KEY_PATH"
    echo "SSH key loaded into agent"
  fi
else
  echo "SSH key not found at $KEY_PATH — skipping ssh-add"
fi

echo "SSH setup complete"