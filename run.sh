#!/bin/bash
# Supply Chain Guardian - Quick Run Script for Linux/Mac

echo "================================================"
echo "  Supply Chain Guardian - Quick Start"
echo "================================================"
echo ""

# Check if virtualenv exists
if [ ! -d "virtualenv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv virtualenv
    echo ""
fi

# Activate virtualenv
echo "Activating virtual environment..."
source virtualenv/bin/activate
echo ""

# Check if requirements are installed
python -c "import vertexai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    echo ""
fi

# Check if database exists
if [ ! -f "supply_chain.db" ]; then
    echo "Initializing database..."
    python setup_database.py
    echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create .env file from .env.example"
    echo ""
    read -p "Press Enter to continue..."
fi

# Show menu
while true; do
    echo ""
    echo "================================================"
    echo "  What would you like to do?"
    echo "================================================"
    echo ""
    echo "  1. Test agents locally (python main.py)"
    echo "  2. Launch Streamlit dashboard"
    echo "  3. Run alert check"
    echo "  4. Initialize/reset database"
    echo "  5. Deploy to Google Cloud"
    echo "  6. Exit"
    echo ""
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            echo ""
            echo "Running agent tests..."
            python main.py
            echo ""
            read -p "Press Enter to continue..."
            ;;
        2)
            echo ""
            echo "Launching Streamlit dashboard..."
            echo "Access the UI at: http://localhost:8501"
            echo "Press Ctrl+C to stop"
            echo ""
            streamlit run ui/app.py
            break
            ;;
        3)
            echo ""
            echo "Running alert check..."
            python alerting.py
            echo ""
            read -p "Press Enter to continue..."
            ;;
        4)
            echo ""
            echo "Initializing database..."
            python setup_database.py
            echo ""
            read -p "Press Enter to continue..."
            ;;
        5)
            echo ""
            echo "Deploying to Google Cloud..."
            echo "Make sure GOOGLE_CLOUD_PROJECT and STAGING_BUCKET are set in .env"
            echo ""
            python deploy.py
            echo ""
            read -p "Press Enter to continue..."
            ;;
        6)
            break
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac
done

echo ""
echo "Thank you for using Supply Chain Guardian!"
echo ""
