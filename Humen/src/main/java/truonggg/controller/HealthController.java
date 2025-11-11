package truonggg.controller;

import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import truonggg.response.SuccessReponse;

@RestController
@RequestMapping("/api/v1")
public class HealthController {

	@GetMapping("/health")
	public SuccessReponse<Map<String, Object>> health() {
		return SuccessReponse.of(Map.of("status", "UP"));
	}
}



