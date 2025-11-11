package truonggg.handler;

import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import jakarta.validation.ConstraintViolationException;
import truonggg.exception.NotFoundException;
import truonggg.exception.UserAlreadyExistException;
import truonggg.response.ErrorCode;
import truonggg.response.ErrorReponse;

@RestControllerAdvice
public class GlobalExceptionHandler {
	@ResponseStatus(value = HttpStatus.NOT_FOUND)
	@ExceptionHandler(exception = { NotFoundException.class })
	public ErrorReponse handle(final NotFoundException ex) {
		return ErrorReponse.of(ex.getMessage(), ex.getErrorCode(), ex.getDomain());
	}

	@ResponseStatus(value = HttpStatus.INTERNAL_SERVER_ERROR)
	@ExceptionHandler(exception = { Exception.class })
	public ErrorReponse handle(final Exception ex) {
		return ErrorReponse.of(ex.getMessage(), ErrorCode.INTERNAL_SERVER, "system");
	}

	@ResponseStatus(value = HttpStatus.BAD_REQUEST)
	@ExceptionHandler(exception = { MethodArgumentNotValidException.class })
	public ErrorReponse handle(final MethodArgumentNotValidException exception) {
		Map<String, Object> details = exception.getBindingResult().getFieldErrors().stream()
				.collect(Collectors.toMap(x -> x.getField().toString(), x -> x.getDefaultMessage(), (a, b) -> b));

		return ErrorReponse.of("Validation failed", ErrorCode.INVALID, "request", details);

	}

	@ResponseStatus(HttpStatus.CONFLICT) // 409 trùng dữ liệu
	@ExceptionHandler(UserAlreadyExistException.class)
	public ErrorReponse handleUserAlreadyExist(UserAlreadyExistException ex) {
		Map<String, Object> details = Map.of("field", ex.getMessage().contains("userName") ? "userName" : "email");

		return ErrorReponse.of(ex.getMessage(), ex.getErrorCode(), ex.getDomain(), details);
	}

	@ResponseStatus(value = HttpStatus.BAD_REQUEST)
	@ExceptionHandler(exception = { ConstraintViolationException.class })
	public ErrorReponse handle(final ConstraintViolationException exception) {
		Map<String, Object> details = exception.getConstraintViolations().stream()
				.collect(Collectors.toMap(x -> x.getPropertyPath().toString(), x -> x.getMessage(), (a, b) -> b));

		return ErrorReponse.of("Validation failed", ErrorCode.INVALID, "request", details);
	}
}