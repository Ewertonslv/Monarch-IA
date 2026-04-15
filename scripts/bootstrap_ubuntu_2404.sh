#!/usr/bin/env bash
set -euo pipefail

echo "[1/6] Atualizando pacotes base"
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release git

echo "[2/6] Preparando keyring do Docker"
sudo install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.asc ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
  sudo chmod a+r /etc/apt/keyrings/docker.asc
fi

echo "[3/6] Adicionando repositório oficial do Docker"
ARCH="$(dpkg --print-architecture)"
CODENAME="$(. /etc/os-release && echo "${VERSION_CODENAME}")"
echo \
  "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${CODENAME} stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "[4/6] Instalando Docker Engine e Compose Plugin"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "[5/6] Habilitando serviço do Docker"
sudo systemctl enable docker
sudo systemctl start docker

echo "[6/6] Adicionando usuário atual ao grupo docker"
sudo usermod -aG docker "$USER"

echo
echo "Bootstrap concluído."
echo "Faça logout/login antes de usar docker sem sudo."
