
#!/bin/bash

echo "正在清理旧的 NVIDIA 驱动和 CUDA 安装..."
sudo apt-get purge nvidia-* cuda-* -y
sudo apt-get autoremove -y

echo "正在下载并安装 NVIDIA 存储库的 GPG 密钥..."
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb

# 2. 更新本地软件源
sudo apt-get update

echo "正在安装 CUDA Toolkit 12.4..."
sudo apt-get -y install cuda-toolkit-12-4

cat EOF >> ~/.bashrc <<EOF
export CUDA_HOME=/usr/local/cuda-12.4
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
EOF

source ~/.bashrc

echo "Clone llama.cpp ..."
rm -rf llama.cpp
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp

echo "Start building ..."
cmake -B build
cmake --build build --config Release