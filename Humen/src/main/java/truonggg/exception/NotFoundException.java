package truonggg.exception;

import lombok.Getter;
import lombok.Setter;
import truonggg.response.ErrorCode;

@Getter
@Setter
public class NotFoundException extends RuntimeException {

	private static final long serialVersionUID = 1L;

	private final ErrorCode errorCode = ErrorCode.NOT_FOUND;
	private final String domain; // linh hoạt
	private String message;

	// Constructor mặc định domain = "user"
	public NotFoundException(final String message) {
		this("user", message);
	}

	// Constructor linh hoạt domain
	public NotFoundException(final String domain, final String message) {
		super(message);
		this.domain = domain;
		this.message = message;
	}
}