#!/bin/bash
# DALS Server Management Script

SCRIPT_DIR="/media/spruked/External1TB/Digital Assets Logistics Systems"
SERVICE_NAME="dals"
SERVICE_FILE="$SCRIPT_DIR/dals.service"

case "$1" in
    start)
        echo "Starting DALS server..."
        cd "$SCRIPT_DIR"
        python3 start_server.py
        ;;
    
    install-service)
        echo "Installing DALS as systemd service..."
        sudo cp "$SERVICE_FILE" /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable dals
        echo "Service installed. Use 'sudo systemctl start dals' to start."
        ;;
    
    service-start)
        echo "Starting DALS service..."
        sudo systemctl start dals
        ;;
        
    service-stop)
        echo "Stopping DALS service..."
        sudo systemctl stop dals
        ;;
        
    service-status)
        echo "DALS service status:"
        sudo systemctl status dals
        ;;
        
    service-logs)
        echo "DALS service logs:"
        sudo journalctl -u dals -f
        ;;
        
    *)
        echo "Usage: $0 {start|install-service|service-start|service-stop|service-status|service-logs}"
        echo ""
        echo "Commands:"
        echo "  start            - Run DALS server directly"
        echo "  install-service  - Install DALS as systemd service"
        echo "  service-start    - Start DALS service"
        echo "  service-stop     - Stop DALS service"
        echo "  service-status   - Check DALS service status"
        echo "  service-logs     - View DALS service logs"
        ;;
esac