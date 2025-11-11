from typing import Any, Dict, Optional
from datetime import datetime


def wrap_success(data: Any, trace_id: Optional[str] = None) -> Dict[str, Any]:
	return {
		"operationType": "Success",
		"message": "success",
		"code": "OK",
		"data": data,
		"size": len(data) if isinstance(data, (list, tuple, set)) else 0,
		"traceId": trace_id,
		"thời gian": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	}


def wrap_error(code: str, message: str, domain: Optional[str] = None, details: Optional[Dict[str, Any]] = None, trace_id: Optional[str] = None) -> Dict[str, Any]:
	return {
		"operationType": "Failure",
		"message": message,
		"code": code,
		"domain": domain,
		"details": details,
		"traceId": trace_id,
		"thời gian": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	}



