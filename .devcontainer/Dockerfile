FROM python:3.13-slim

# Setup workspace directory
RUN mkdir /workspace
WORKDIR /workspace

# Set Python path
ENV PYTHONPATH=/workspace/backend

# Install useful system utilities
ENV TZ=America/New_York
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --yes \
        apt-transport-https \
        ca-certificates \
        curl \
        debian-keyring \
        debian-archive-keyring \
        git \
        gnupg \
        locales \
        sudo \
        tzdata \
        wget \
        net-tools \
        procps \
        socat \
        iproute2 \
        libicu-dev \
    && rm -rf /var/lib/apt/lists/*

# Install SQL Server tools
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y mssql-tools18 unixodbc-dev \
    && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> /etc/bash.bashrc \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 24 from https://github.com/nodesource
ENV NODE_MAJOR=24
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install nodejs -y \
    && npm install -g npm@latest \
    && rm -rf /var/lib/apt/lists/*

# Use a non-root user per https://code.visualstudio.com/remote/advancedcontainers/add-nonroot-user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Add non-root user and add to sudoers
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Git configuration
RUN git config --system core.editor "code --wait" \
    && git config --system safe.directory '/workspace' \
    && git config --system push.autoSetupRemote true \
    && git config --system pull.autoSetupRemote true \
    && git config --system init.defaultBranch main \
    && git config --system core.autocrlf input \
    && git config --system color.ui auto

# Install python dev dependencies
RUN pip install --upgrade pip

# Configure locale (must be done as root before switching users)
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Configure bash
USER $USERNAME
ENV HOME=/home/$USERNAME

# Setup bash profile with git branch display
RUN echo 'parse_git_branch() {' >> ~/.bash_profile \
    && echo '  local branch=$(git branch 2>/dev/null | grep "^\*" | cut -d" " -f2)' >> ~/.bash_profile \
    && echo '  if [ -n "$branch" ]; then' >> ~/.bash_profile \
    && echo '    local dirty=""' >> ~/.bash_profile \
    && echo '    [[ -n $(git status --porcelain 2>/dev/null) ]] && dirty="*"' >> ~/.bash_profile \
    && echo '    echo " ($branch$dirty)"' >> ~/.bash_profile \
    && echo '  fi' >> ~/.bash_profile \
    && echo '}' >> ~/.bash_profile \
    && echo '' >> ~/.bash_profile \
    && echo 'export PS1="\T \[\033[32m\]\w\[\033[33m\]\$(parse_git_branch)\[\033[00m\] $ "' >> ~/.bash_profile \
    && echo '' >> ~/.bash_profile \
    && echo 'export PATH=$PATH:$HOME/.local/bin:/workspace/frontend/node_modules/.bin:/opt/mssql-tools18/bin' >> ~/.bash_profile \
    && echo '' >> ~/.bash_profile \
    && echo '[ -f "$HOME/.local/bin/env" ] && . "$HOME/.local/bin/env"' >> ~/.bash_profile \
    && echo '' >> ~/.bash_profile \
    && echo '# Source bash_profile from bashrc for non-login shells' >> ~/.bashrc \
    && echo '[ -f ~/.bash_profile ] && . ~/.bash_profile' >> ~/.bashrc

# Expose application ports
EXPOSE 8000 3000

# Keep the container running
CMD ["tail", "-f", "/dev/null"]
