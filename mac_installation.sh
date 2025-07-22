#!/bin/bash

# Detecting Operating System
OS=$(uname)

cd ~/Downloads/Scraper_App/ || {
  # If the cd fails, rename the directory
  mv ~/Downloads/Scraper_App-main ~/Downloads/Scraper_App && echo "Renamed Scraper_App-main to Scraper_App";
  # Try the cd command again after renaming
  cd ~/Downloads/Scraper_App/ || exit 1;
}

# git config --global http.postBuffer 157286400

## Check if the Scraper_App folder already exists
#if [ -d "Scraper_App" ]; then
#  echo "Scraper_App folder already exists. Pulling latest changes..."
#  cd Scraper_App || exit
#  git pull  # Update the existing repository
#else
#  # Clone the repository if the folder doesn't exist
#  echo "Cloning the repository..."
#  git clone --depth 1 https://github.com/PKING1501/Scraper_App.git
#  cd Scraper_App || exit
#fi

# Create a virtual environment
echo "Creating virtual environment..."
if [[ "$OS" == "Darwin" || "$OS" == "Linux" ]]; then
  # macOS/Linux
  python3 -m venv env
  source env/bin/activate
else
  # Windows (Git Bash or WSL)
  python -m venv env
  source env/Scripts/activate
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
echo "Installing dependencies from req.txt..."
pip install -r req.txt

# Start the backend server inside the virtual environment in a new terminal
echo "Starting the backend server in a new terminal..."
if [[ "$OS" == "Darwin" || "$OS" == "Linux" ]]; then
  # For macOS/Linux, close the current terminal and open a new one to run the backend
  osascript -e 'tell app "Terminal" to do script "cd ~/Downloads/Scraper_App && source env/bin/activate && cd backend && python first.py"'
  osascript -e 'tell app "Terminal" to close current window'  # Close the current terminal window
else
  # For Windows (Git Bash or WSL), close the current terminal and open a new one to run the backend
  start bash -c "cd ~/Downloads/Scraper_App && source env/Scripts/activate && cd backend && python first.py"
  exit 0  # Close the current terminal after running the backend
fi

# Open a new terminal for the frontend
if [[ "$OS" == "Darwin" || "$OS" == "Linux" ]]; then
  # For macOS/Linux, open a new terminal and run the frontend setup
  osascript -e 'tell app "Terminal" to do script "cd ~/Downloads/Scraper_App/frontend && npm install --legacy-peer-deps && npm start"'
else
  # For Windows, open Git Bash or WSL terminal and run the frontend setup
  start bash -c "cd ~/Downloads/Scraper_App/frontend && npm install --legacy-peer-deps && npm start"
fi

echo "Frontend and backend servers are now running."
