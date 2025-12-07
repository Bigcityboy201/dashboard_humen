package truonggg.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import truonggg.dto.request.User.UpdateProfileRequestDTO;
import truonggg.dto.response.UserResponseDTO;
import truonggg.response.SuccessReponse;
import truonggg.sercurity.CustomUserDetails;
import truonggg.service.UserService;

@RestController
@RequestMapping("/profile")
@RequiredArgsConstructor
@PreAuthorize("hasAnyRole('ADMIN', 'HR_MANAGER')")
public class ProfileController {

	private final UserService userService;

	@GetMapping
	public SuccessReponse<UserResponseDTO> getProfile() {
		// Lấy user hiện tại từ SecurityContext
		Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
		CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
		String username = userDetails.getUsername();

		UserResponseDTO profile = userService.getCurrentUserProfile(username);
		return SuccessReponse.of(profile);
	}

	@PutMapping
	public SuccessReponse<UserResponseDTO> updateProfile(@RequestBody @Valid UpdateProfileRequestDTO dto) {
		// Lấy user hiện tại từ SecurityContext
		Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
		CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
		String username = userDetails.getUsername();

		UserResponseDTO updatedProfile = userService.updateCurrentUserProfile(username, dto);
		return SuccessReponse.of(updatedProfile);
	}

	@PutMapping("/change-password")
	public SuccessReponse<UserResponseDTO> changePassword(@RequestBody @Valid truonggg.dto.request.User.ChangePasswordRequestDTO dto) {
		// Lấy user hiện tại từ SecurityContext
		Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
		CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
		String username = userDetails.getUsername();

		UserResponseDTO updatedProfile = userService.changePassword(username, dto);
		return SuccessReponse.of(updatedProfile);
	}
}

