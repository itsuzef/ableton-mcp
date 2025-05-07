"""
Analyzer Handler for Ableton MCP Server

This module handles the integration between the Audio Analyzer plugin and the Ableton MCP server.
It receives OSC messages from the plugin and makes the analysis data available through the MCP API.
"""

import json
import logging
import threading
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AnalyzerHandler")

# Try to import python-osc, but make it optional
try:
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import BlockingOSCUDPServer
    OSC_AVAILABLE = True
except ImportError:
    logger.warning("python-osc is not installed. Audio analyzer features will be disabled.")
    OSC_AVAILABLE = False

class AnalyzerHandler:
    """Handler for Audio Analyzer plugin data"""
    
    def __init__(self, osc_port: int = 8888):
        """Initialize the analyzer handler"""
        self.osc_port = osc_port
        self.latest_data: Dict[str, Any] = {}
        self.data_lock = threading.Lock()
        self.server = None
        self.server_thread = None
        self.running = False
        
    def start(self) -> bool:
        """Start the OSC server to receive analyzer data"""
        if self.running:
            return True
            
        if not OSC_AVAILABLE:
            logger.warning("Audio analyzer disabled: python-osc not installed")
            return False
            
        try:
            # Create dispatcher
            dispatcher = Dispatcher()
            dispatcher.map("/mcp/analyzer", self._handle_analyzer_data)
            
            # Create server
            self.server = BlockingOSCUDPServer(("127.0.0.1", self.osc_port), dispatcher)
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            logger.info(f"Analyzer handler started on port {self.osc_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start analyzer handler: {str(e)}")
            return False
    
    def stop(self):
        """Stop the OSC server"""
        if self.server and self.running:
            self.running = False
            if self.server:
                self.server.shutdown()
            if self.server_thread:
                self.server_thread.join(timeout=1.0)
            logger.info("Analyzer handler stopped")
    
    def _run_server(self):
        """Run the OSC server"""
        try:
            logger.info(f"OSC server listening on port {self.osc_port}")
            self.server.serve_forever()
        except Exception as e:
            if self.running:  # Only log if we didn't intentionally stop
                logger.error(f"OSC server error: {str(e)}")
    
    def _handle_analyzer_data(self, address, *args):
        """Handle incoming analyzer data"""
        try:
            if len(args) < 1:
                logger.warning(f"Received analyzer data with insufficient arguments: {args}")
                return
                
            # Parse JSON data
            json_data = args[0]
            data = json.loads(json_data)
            
            # Store data with timestamp
            with self.data_lock:
                track_name = data.get("track_name", "unknown")
                self.latest_data[track_name] = {
                    "timestamp": time.time(),
                    "data": data
                }
                
            logger.debug(f"Received analyzer data for track: {track_name}")
        except Exception as e:
            logger.error(f"Error handling analyzer data: {str(e)}")
    
    def get_latest_data(self, track_name: Optional[str] = None) -> Dict[str, Any]:
        """Get the latest analyzer data"""
        with self.data_lock:
            if track_name:
                # Return data for specific track
                track_data = self.latest_data.get(track_name)
                if track_data:
                    return {track_name: track_data}
                return {}
            else:
                # Return all data
                return self.latest_data.copy()
    
    def get_track_analysis(self, track_name: str) -> Dict[str, Any]:
        """Get analysis for a specific track"""
        if not OSC_AVAILABLE:
            return {"error": "Audio analyzer is disabled. Install python-osc to enable this feature."}
            
        with self.data_lock:
            track_data = self.latest_data.get(track_name)
            if not track_data:
                return {"error": f"No analysis data available for track: {track_name}"}
                
            # Check if data is fresh (less than 5 seconds old)
            if time.time() - track_data["timestamp"] > 5.0:
                return {
                    "warning": "Analysis data may be stale",
                    "data": track_data["data"]
                }
                
            return track_data["data"]

# Singleton instance
_analyzer_handler = None

def get_analyzer_handler(osc_port: int = 8888) -> AnalyzerHandler:
    """Get or create the analyzer handler singleton"""
    global _analyzer_handler
    if _analyzer_handler is None:
        _analyzer_handler = AnalyzerHandler(osc_port)
    return _analyzer_handler
