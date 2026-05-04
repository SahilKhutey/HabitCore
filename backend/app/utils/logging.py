import logging
import json
from datetime import datetime, timezone

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Simple JSON formatter if python-json-logger isn't fully set up yet
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)
    
    def _format(self, level, message, **kwargs):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        return json.dumps(log_entry)

    def info(self, message, **kwargs):
        print(self._format("INFO", message, **kwargs))
    
    def warning(self, message, **kwargs):
        print(self._format("WARNING", message, **kwargs))
    
    def error(self, message, **kwargs):
        print(self._format("ERROR", message, **kwargs))

# Global logger instance
structured_logger = StructuredLogger("habit-orchestrator")
