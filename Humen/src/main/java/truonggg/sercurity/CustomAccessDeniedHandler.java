package truonggg.sercurity;

import java.io.IOException;

import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import truonggg.response.ErrorCode;
import truonggg.response.ErrorReponse;

@Component
@RequiredArgsConstructor
public class CustomAccessDeniedHandler implements AccessDeniedHandler {
	private final ObjectMapper objectMapper;

	@Override
	public void handle(HttpServletRequest request, HttpServletResponse response,
			AccessDeniedException accessDeniedException) throws IOException, ServletException {
		if (response.isCommitted()) {
			return;
		}

		try {
			response.setStatus(HttpServletResponse.SC_FORBIDDEN);
			response.setContentType("application/json");
			response.setCharacterEncoding("UTF-8");

			ErrorReponse errorResponse = ErrorReponse.of("You do not have permission to access this resource",
					ErrorCode.INVALID, "security");

			if (objectMapper != null) {
				String jsonResponse = objectMapper.writeValueAsString(errorResponse);
				response.getWriter().write(jsonResponse);
			} else {
				// Fallback nếu ObjectMapper null
				response.getWriter().write(
						"{\"message\":\"You do not have permission to access this resource\",\"code\":\"INVALID\",\"domain\":\"security\",\"operationType\":\"Failure\"}");
			}
			response.getWriter().flush();
		} catch (Exception e) {
			// Fallback nếu có lỗi với ObjectMapper
			if (!response.isCommitted()) {
				response.setStatus(HttpServletResponse.SC_FORBIDDEN);
				response.setContentType("application/json");
				response.setCharacterEncoding("UTF-8");
				response.getWriter().write(
						"{\"message\":\"You do not have permission to access this resource\",\"code\":\"INVALID\",\"domain\":\"security\",\"operationType\":\"Failure\"}");
				response.getWriter().flush();
			}
		}
	}
}
