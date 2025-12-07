package truonggg.controller;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import truonggg.dto.request.User.AdminUpdateUserRequestDTO;
import truonggg.dto.request.User.UserRequestDTO;
import truonggg.dto.request.User.UserUpdate_Active_RequestDTO;
import truonggg.dto.response.UserResponseDTO;
import truonggg.response.PagedResult;
import truonggg.response.SuccessReponse;
import truonggg.service.UserService;

@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
@PreAuthorize("hasRole('ADMIN')")
public class UserController {

	private final UserService userService;

	@GetMapping
	@PreAuthorize("hasRole('ADMIN')")
	public SuccessReponse<?> getAll(@RequestParam(value = "page", defaultValue = "0") int page,
			@RequestParam(value = "size", defaultValue = "10") int size) {
		Pageable pageable = PageRequest.of(page, size);
		PagedResult<UserResponseDTO> pagedResult = this.userService.getAll(pageable);
		return SuccessReponse.ofPaged(pagedResult);
	}

	@PostMapping
	@PreAuthorize("hasRole('ADMIN')")
	public SuccessReponse<?> save(@RequestBody @Valid UserRequestDTO dto) {
		return SuccessReponse.of(this.userService.save(dto));
	}

	@PutMapping("/{id}")
	@PreAuthorize("hasRole('ADMIN')")
	public SuccessReponse<UserResponseDTO> updateUser(@PathVariable Integer id,
			@Valid @RequestBody AdminUpdateUserRequestDTO dto) {
		return SuccessReponse.of(userService.updateUserByAdmin(id, dto));
	}

	@PutMapping("/{id}/status")
	@PreAuthorize("hasRole('ADMIN')")
	public SuccessReponse<UserResponseDTO> updateStatus(@PathVariable Integer id,
			@Valid @RequestBody UserUpdate_Active_RequestDTO dto) {

		return SuccessReponse.of(userService.updateStatus(id, dto));
	}

	@DeleteMapping("/{id}")
	@PreAuthorize("hasRole('ADMIN')")
	public SuccessReponse<String> deleteManually(@PathVariable Integer id) {
		this.userService.deleteManually(id);
		return SuccessReponse.of("Xóa thành công user with id: " + id);
	}

	@PutMapping("/{id}/reset-password")
	@PreAuthorize("hasRole('ADMIN')")
	public SuccessReponse<UserResponseDTO> resetPassword(@PathVariable Integer id,
			@RequestBody java.util.Map<String, String> request) {
		String newPassword = request.get("password");
		if (newPassword == null || newPassword.trim().isEmpty()) {
			throw new IllegalArgumentException("Password không được để trống");
		}
		return SuccessReponse.of(userService.resetPassword(id, newPassword));
	}
}
