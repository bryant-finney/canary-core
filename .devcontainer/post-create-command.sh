#!/bin/sh
# install system packages
apt update && apt install -y zsh jq gnupg2 git docker docker-compose vim neovim

curl -L https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh --output install.sh &&
	chmod +x install.sh && ./install.sh &&
	rm install.sh

test -f ~/.zshrc.new && cp ~/.zshrc.new ~/.zshrc

git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/powerlevel10k &&
	echo 'source ~/powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc
