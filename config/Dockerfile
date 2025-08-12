FROM python:3.13.5-slim-bullseye

ARG WORKSPACE_FOLDER_NAME=default
ENV WORKSPACE_FOLDER_NAME=$WORKSPACE_FOLDER_NAME

ENV HOME_FOLDER=/workspaces/$WORKSPACE_FOLDER_NAME
WORKDIR $HOME_FOLDER
ENV TEMPFOLDER=/tmp/mytmp

# Install necessary packages and tools
RUN apt-get update && apt-get install -y xdg-utils curl jq unzip git gcc build-essential

# Install Terraform CLI
RUN TERRAFORM_VERSION=$(curl -s https://checkpoint-api.hashicorp.com/v1/check/terraform | jq -r .current_version | sed 's/^v//') \
    && curl -O https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /usr/bin \
    && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Install pyenv
RUN curl https://pyenv.run | bash \
    && echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc \
    && echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc \
    && echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set bash as the default command
CMD ["/bin/bash"]
