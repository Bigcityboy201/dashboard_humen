package truonggg.controller;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import truonggg.dto.request.Role.RoleRequestDTO;
import truonggg.dto.response.RoleResponseDTO;
import truonggg.response.SuccessReponse;
import truonggg.service.RoleService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/roles")
public class RoleController {

	private final RoleService roleService;

	@GetMapping
	public SuccessReponse<List<RoleResponseDTO>> getAll() {
		return SuccessReponse.of(this.roleService.getAll());
	}

	@PostMapping
	public SuccessReponse<RoleResponseDTO> save(@RequestBody @Valid final RoleRequestDTO dto) {
		return SuccessReponse.of(this.roleService.save(dto));
	}
}
