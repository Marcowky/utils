VERSION=0.4.19
VSCODE_PATH=/home/kaiyu/usr/kaiyu

cd "$VSCODE_PATH/.vscode-server/extensions/openai.chatgpt-$VERSION-linux-x64/bin/linux-x86_64"

# keep the original
mv codex codex.real

# wrapper that forces a proxy and then calls the original
cat > codex <<'EOF'
#!/usr/bin/env bash
export HTTPS_PROXY="http://127.0.0.1:7890"
export HTTP_PROXY="http://127.0.0.1:7890"
export NO_PROXY="localhost,127.0.0.1,::1"
# ------------------------------------------------
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "$HERE/codex.real" "$@"
EOF
chmod +x codex
