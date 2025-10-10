# This script allows to use ssh as authentication
# The ssh keys must be previously configured in your local machine 
# Once this script is done, configure git to know who are you with
#
#  - git config --global user.name "Your name"
#  - git config --global user.email "your_email@email.com"
#  - git config --global user.signingkey $HOME/.ssh/ssh_key_name.pub

#!/bin/bash
set -euo pipefail

echo "Setting up SSH config and Git signing..."

# Define paths
SSH_DIR="$HOME/.ssh"
SSH_CONFIG_SRC="$SSH_DIR/config"
SSH_CONFIG_SAFE="$SSH_DIR/config-devcontainer"
KEY_PATH="$SSH_DIR/id_ed25519"

# 1. Copy SSH config if it exists
if [[ -f "$SSH_CONFIG_SRC" ]]; then
  cp "$SSH_CONFIG_SRC" "$SSH_CONFIG_SAFE"
  chmod 600 "$SSH_CONFIG_SAFE"
  echo "Copied SSH config to $SSH_CONFIG_SAFE"
else
  echo "SSH config not found at $SSH_CONFIG_SRC — skipping copy"
fi

# 2. Configure Git to use the safe copy if it exists
if [[ -f "$SSH_CONFIG_SAFE" ]]; then
  git config --global core.sshCommand "ssh -F $SSH_CONFIG_SAFE"
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