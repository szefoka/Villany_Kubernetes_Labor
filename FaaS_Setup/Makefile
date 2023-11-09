install:
	dhclient enp0s8
	@if [ -z "$$(which ansible)" ]; then \
		sudo apt update -y && \
		sudo apt install software-properties-common -y && \
		sudo add-apt-repository --yes --update ppa:ansible/ansible && \
		sudo apt install ansible -y; \
	fi
	ansible-playbook playbook.yaml
reset:
	dhclient enp0s8
	ansible-playbook kubeinit.yaml
