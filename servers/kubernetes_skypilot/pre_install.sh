# MacOS
brew install kubectl socat netcat

# Linux (may have socat already installed)
sudo apt-get install kubectl socat netcat
go install sigs.k8s.io/kind@v0.22.0 && kind create cluster
pip3 install "skypilot[all]"

# Copy kubeconfig
mkdir -p ~/.kube
cp /path/to/kubeconfig ~/.kube/config