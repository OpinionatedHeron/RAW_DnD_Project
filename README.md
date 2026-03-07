# RAW_DnD_Project
Project to investigate the use of Large Language Models and Retrieval-Augmented Generation frameworks as a rule-assistance tool for Tabletop Role-Playing Games (TTRPGs) with a specific focus on Dungeons and Dragons 5th Edition. Test based development and investigation.

## Setup Environment
Following commands for Ubuntu Linux

1. Update packages
    <!---TODO: Add explanations for each section--->
    ```bash
    sudo apt update
    sudo apt full-upgrade -y
    ```

2. Install Python 3.11 and venv
    ```bash
    sudo apt install python3.11 python3.11-venv python3-pip
    ```
    Verify your python installation
    ```bash
    python3.11 --version
    ```

3. Build tools - required for InstructlLab native extensions
    ```bash
    sudo apt install build-essential
    ```

4. Install extra build dependencies
    ```bash
    sudo apt install gcc g++ make libssl-dev libffi-dev zlib1g-dev
    ```