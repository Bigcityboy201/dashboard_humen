package truonggg.controller;

import java.net.ConnectException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import truonggg.response.ErrorCode;
import truonggg.response.ErrorReponse;
import truonggg.trace.TraceIdContext;

@RestController
@RequestMapping("/api/python")
@RequiredArgsConstructor
public class PythonProxyController {

	@Value("${python.api.base-url:http://localhost:5000}")
	private String pythonApiBaseUrl;

	private final RestTemplate restTemplate;

	@RequestMapping("/**")
	public ResponseEntity<?> proxyRequest(HttpServletRequest request, @RequestBody(required = false) String body) {
		try {
			// Lấy path từ request
			String requestPath = request.getRequestURI();
			String pythonPath = requestPath.replace("/api/python", "");

			// Xây dựng URL đầy đủ
			String queryString = request.getQueryString();
			String fullUrl = pythonApiBaseUrl + pythonPath + (queryString != null ? "?" + queryString : "");
			URI uri = new URI(fullUrl);

			// Copy headers từ request gốc
			HttpHeaders headers = new HttpHeaders();
			Enumeration<String> headerNames = request.getHeaderNames();
			while (headerNames.hasMoreElements()) {
				String headerName = headerNames.nextElement();
				// Bỏ qua một số headers không cần thiết
				if (!headerName.equalsIgnoreCase("host") && !headerName.equalsIgnoreCase("content-length")
						&& !headerName.equalsIgnoreCase("connection")) {
					headers.add(headerName, request.getHeader(headerName));
				}
			}

			// Tạo request entity với body nếu có
			HttpEntity<String> entity = new HttpEntity<>(body != null ? body : null, headers);

			// Forward request sang Python API
			HttpMethod method = HttpMethod.valueOf(request.getMethod());
			
			// Forward request sang Python API
			// Sử dụng Object.class để RestTemplate tự động deserialize JSON
			ResponseEntity<Object> response = restTemplate.exchange(uri, method, entity, Object.class);

			// Tạo lại response headers, loại bỏ Content-Length để Spring tự tính lại
			HttpHeaders responseHeaders = new HttpHeaders();
			
			// Đảm bảo Content-Type là application/json với UTF-8
			MediaType contentType = response.getHeaders().getContentType();
			if (contentType == null) {
				contentType = MediaType.APPLICATION_JSON;
			}
			// Tạo MediaType mới với charset UTF-8
			MediaType utf8ContentType = new MediaType(contentType.getType(), contentType.getSubtype(), java.nio.charset.StandardCharsets.UTF_8);
			responseHeaders.setContentType(utf8ContentType);
			
			// Không copy Content-Length và Transfer-Encoding, để Spring tự tính lại dựa trên body thực tế
			// Copy các headers khác nếu cần (trừ Content-Length và Transfer-Encoding)
			response.getHeaders().forEach((key, values) -> {
				String lowerKey = key.toLowerCase();
				if (!lowerKey.equals("content-length") && !lowerKey.equals("transfer-encoding")) {
					responseHeaders.put(key, values);
				}
			});

			return new ResponseEntity<>(response.getBody(), responseHeaders, response.getStatusCode());

		} catch (ResourceAccessException e) {
			// Xử lý lỗi kết nối (Connection refused, timeout, etc.)
			Throwable cause = e.getCause();
			String errorMessage = "Không thể kết nối đến Python API server";
			String detailMessage = e.getMessage();

			if (cause instanceof ConnectException) {
				errorMessage = "Python API server không khả dụng. Vui lòng kiểm tra server đã chạy chưa.";
				detailMessage = "Connection refused: " + pythonApiBaseUrl;
			}

			Map<String, Object> details = new HashMap<>();
			details.put("error", detailMessage);
			details.put("pythonApiUrl", pythonApiBaseUrl);

			ErrorReponse errorResponse = ErrorReponse.builder()
					.message(errorMessage)
					.code(ErrorCode.INTERNAL_SERVER)
					.domain("python-proxy")
					.details(details)
					.traceId(TraceIdContext.get())
					.build();

			return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(errorResponse);

		} catch (RestClientException e) {
			// Xử lý các lỗi RestClient khác
			Map<String, Object> details = new HashMap<>();
			details.put("error", e.getMessage());
			details.put("pythonApiUrl", pythonApiBaseUrl);

			ErrorReponse errorResponse = ErrorReponse.builder()
					.message("Lỗi khi gọi Python API")
					.code(ErrorCode.INTERNAL_SERVER)
					.domain("python-proxy")
					.details(details)
					.traceId(TraceIdContext.get())
					.build();

			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);

		} catch (URISyntaxException e) {
			// Xử lý lỗi URI không hợp lệ
			Map<String, Object> details = new HashMap<>();
			details.put("error", e.getMessage());

			ErrorReponse errorResponse = ErrorReponse.builder()
					.message("URL không hợp lệ")
					.code(ErrorCode.INVALID)
					.domain("python-proxy")
					.details(details)
					.traceId(TraceIdContext.get())
					.build();

			return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);

		} catch (Exception e) {
			// Xử lý các lỗi khác
			Map<String, Object> details = new HashMap<>();
			details.put("error", e.getMessage());
			details.put("exceptionType", e.getClass().getName());

			ErrorReponse errorResponse = ErrorReponse.builder()
					.message("Lỗi không xác định khi proxy request")
					.code(ErrorCode.INTERNAL_SERVER)
					.domain("python-proxy")
					.details(details)
					.traceId(TraceIdContext.get())
					.build();

			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
		}
	}
}

