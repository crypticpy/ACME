"""Audit logging system for full traceability."""

import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import settings


class AuditLogger:
    """Comprehensive audit logging for data lineage and traceability."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.audit_file = settings.audit_dir / f"audit_log_{self.session_id}.jsonl"
        self.audit_file.parent.mkdir(exist_ok=True, parents=True)
        
        # Initialize session
        self.log_operation(
            operation="session_start",
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            config=self._sanitize_config()
        )
    
    def log_operation(self, operation: str, **kwargs) -> str:
        """Log an operation with full context."""
        entry = {
            "id": str(uuid.uuid4()),
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "data": kwargs
        }
        
        # Add data hash if applicable
        if "data_hash" not in entry["data"] and "data" in kwargs:
            entry["data"]["data_hash"] = self._hash_data(kwargs["data"])
        
        # Write to audit log
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(entry, default=str) + '\n')
        
        return entry["id"]
    
    def log_transformation(
        self, 
        operation: str,
        input_data: Any,
        output_data: Any,
        parameters: Dict[str, Any]
    ) -> str:
        """Log a data transformation with before/after hashes."""
        return self.log_operation(
            operation=operation,
            input_hash=self._hash_data(input_data),
            output_hash=self._hash_data(output_data),
            parameters=parameters,
            transformation_type="data_transformation"
        )
    
    def log_llm_call(
        self,
        prompt: str,
        response: str,
        model: str,
        parameters: Dict[str, Any],
        tokens_used: Optional[Dict[str, int]] = None
    ) -> str:
        """Log LLM API calls for reproducibility."""
        return self.log_operation(
            operation="llm_call",
            model=model,
            prompt_hash=self._hash_data(prompt),
            response_hash=self._hash_data(response),
            parameters=parameters,
            tokens_used=tokens_used,
            prompt_preview=prompt[:200] + "..." if len(prompt) > 200 else prompt
        )
    
    def log_validation(
        self,
        dataset: str,
        validation_type: str,
        result: bool,
        details: Dict[str, Any]
    ) -> str:
        """Log data validation results."""
        return self.log_operation(
            operation="validation",
            dataset=dataset,
            validation_type=validation_type,
            result=result,
            details=details
        )
    
    def log_error(
        self,
        operation: str,
        error_type: str,
        error_message: str,
        context: Dict[str, Any]
    ) -> str:
        """Log errors with context."""
        return self.log_operation(
            operation="error",
            error_operation=operation,
            error_type=error_type,
            error_message=error_message,
            context=context
        )
    
    def log_warning(
        self,
        operation: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log warnings with context."""
        return self.log_operation(
            operation="warning",
            warning_operation=operation,
            message=message,
            context=context or {}
        )
    
    def create_lineage_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Create a data lineage report from audit logs."""
        entries = []
        
        with open(self.audit_file, 'r') as f:
            for line in f:
                entries.append(json.loads(line))
        
        # Build lineage graph
        lineage = {
            "session_id": self.session_id,
            "start_time": entries[0]["timestamp"] if entries else None,
            "end_time": entries[-1]["timestamp"] if entries else None,
            "operations": len(entries),
            "transformations": [],
            "validations": [],
            "llm_calls": [],
            "errors": []
        }
        
        for entry in entries:
            if entry["data"].get("transformation_type") == "data_transformation":
                lineage["transformations"].append({
                    "operation": entry["operation"],
                    "timestamp": entry["timestamp"],
                    "input_hash": entry["data"]["input_hash"],
                    "output_hash": entry["data"]["output_hash"]
                })
            elif entry["operation"] == "validation":
                lineage["validations"].append({
                    "dataset": entry["data"]["dataset"],
                    "type": entry["data"]["validation_type"],
                    "result": entry["data"]["result"],
                    "timestamp": entry["timestamp"]
                })
            elif entry["operation"] == "llm_call":
                lineage["llm_calls"].append({
                    "model": entry["data"]["model"],
                    "timestamp": entry["timestamp"],
                    "tokens": entry["data"].get("tokens_used")
                })
            elif entry["operation"] == "error":
                lineage["errors"].append({
                    "operation": entry["data"]["error_operation"],
                    "type": entry["data"]["error_type"],
                    "message": entry["data"]["error_message"],
                    "timestamp": entry["timestamp"]
                })
        
        # Save report if requested
        if output_file:
            output_file.parent.mkdir(exist_ok=True, parents=True)
            with open(output_file, 'w') as f:
                json.dump(lineage, f, indent=2)
        
        return lineage
    
    def _hash_data(self, data: Any) -> str:
        """Create a hash of data for integrity checking."""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)
        
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _sanitize_config(self) -> Dict[str, Any]:
        """Get sanitized configuration (no secrets)."""
        config = {}
        for key, value in settings.model_dump().items():
            if "key" not in key.lower() and "secret" not in key.lower():
                config[key] = value
        return config
    
    def close(self):
        """Close the audit session."""
        self.log_operation(
            operation="session_end",
            session_id=self.session_id,
            timestamp=datetime.now().isoformat()
        )