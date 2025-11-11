package truonggg.filter;

import java.io.IOException;
import java.util.UUID;

import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import truonggg.trace.TraceIdContext;

@Component
@Order(1)
public class RequestTracingFilter extends OncePerRequestFilter {
	public static final String HEADER_REQUEST_ID = "X-Request-Id";

	@Override
	protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
			throws ServletException, IOException {
		String traceId = request.getHeader(HEADER_REQUEST_ID);
		if (traceId == null || traceId.isBlank()) {
			traceId = UUID.randomUUID().toString();
		}

		TraceIdContext.set(traceId);
		response.setHeader(HEADER_REQUEST_ID, traceId);

		try {
			filterChain.doFilter(request, response);
		} finally {
			TraceIdContext.clear();
		}
	}
}



