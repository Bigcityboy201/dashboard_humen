package truonggg.response;

import java.util.Date;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;
import truonggg.trace.TraceIdContext;

@Getter
@Setter
@Builder
public class ErrorReponse {
	private final OperationType operationType = OperationType.Failure;
	private String message;
	private ErrorCode code;
	private String domain;
	private Map<String, Object> details;
	private String traceId;
	@JsonFormat(timezone = "Asia/Ho_Chi_Minh", pattern = "dd/MM/yyyy HH:mm:ss")
	@JsonProperty(value = "thời gian")
	private final Date timestamp = new Date();

	public static ErrorReponse of(final String message, final ErrorCode code) {
		return ErrorReponse.builder().message(message).code(code).traceId(TraceIdContext.get()).build();
	}

	public static ErrorReponse of(final String message, final ErrorCode code, final String domain) {
		return ErrorReponse.builder().message(message).code(code).domain(domain).traceId(TraceIdContext.get()).build();
	}

	public static ErrorReponse of(final String message, final ErrorCode code, final String domain,
			final Map<String, Object> details) {
		return ErrorReponse.builder().message(message).code(code).domain(domain).details(details).traceId(TraceIdContext.get()).build();
	}
}
