from typing import Any, Dict, Optional, Tuple
import requests


class JavaClient:
	def __init__(self, base_url: str, trace_id: Optional[str] = None, timeout: float = 5.0) -> None:
		self.base_url = base_url.rstrip("/")
		self.trace_id = trace_id
		self.timeout = timeout

	def _headers(self) -> Dict[str, str]:
		headers = {
			"Accept": "application/json"
		}
		if self.trace_id:
			headers["X-Request-Id"] = self.trace_id
		return headers

	def get(self, path: str) -> Tuple[bool, int, Any]:
		url = f"{self.base_url}{path}"
		try:
			resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
			status = resp.status_code
			# Try parse json; if fails keep text
			try:
				body = resp.json()
			except Exception:
				body = {"raw": resp.text}
			ok = 200 <= status < 300
			return ok, status, body
		except requests.RequestException as ex:
			return False, 500, {"exception": str(ex)}



