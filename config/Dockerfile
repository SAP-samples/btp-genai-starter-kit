FROM python:3.12.1

ARG WORKSPACE_FOLDER_NAME=default
ENV WORKSPACE_FOLDER_NAME=$WORKSPACE_FOLDER_NAME

ENV HOME_FOLDER=/workspaces/$WORKSPACE_FOLDER_NAME
WORKDIR $HOME_FOLDER
ENV TEMPFOLDER=/tmp/mytmp

# Provide python packages
COPY ./config/requirements.txt $TEMPFOLDER/requirements.txt

# -------------------------------------------------------------------------------------------------
## Install necessary packages to donwload and install tools
# -------------------------------------------------------------------------------------------------
# Install Terraform CLI
RUN apt-get update && apt-get install -y gnupg software-properties-common jq\
    && wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && gpg --no-default-keyring --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg --fingerprint \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update \
    && apt-get install terraform
# Install all python packages
RUN    pip install --upgrade pip \ 
    && pip install --no-cache-dir -r $TEMPFOLDER/requirements.txt

#COPY ./scripts/package $TEMPFOLDER/scripts/package
#RUN pip install -e $TEMPFOLDER/scripts/package

COPY ./scripts/package $HOME_FOLDER/scripts/package
RUN pip install -e $HOME_FOLDER/scripts/package

CMD ["bash"]
