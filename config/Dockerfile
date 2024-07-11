FROM python:3.12.1-alpine

ARG WORKSPACE_FOLDER_NAME=default
ENV WORKSPACE_FOLDER_NAME=$WORKSPACE_FOLDER_NAME

ENV HOME_FOLDER=/workspaces/$WORKSPACE_FOLDER_NAME
WORKDIR $HOME_FOLDER
ENV TEMPFOLDER=/tmp/mytmp
# Disable virtual env for poetry since we are already in isolated environment
ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

# -------------------------------------------------------------------------------------------------
## Install necessary packages to donwload and install tools
# -------------------------------------------------------------------------------------------------
# Install Terraform CLI
RUN apk update && apk add curl unzip jq git bash build-base libffi-dev openssl-dev \
    && TERRAFORM_VERSION=$(curl -s https://checkpoint-api.hashicorp.com/v1/check/terraform | jq -r .current_version) \
    && curl -O https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /usr/bin \
    && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip
RUN apk add --no-cache xdg-utils

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3

CMD ["sh"]
