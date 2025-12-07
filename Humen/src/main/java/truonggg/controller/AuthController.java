package truonggg.controller;

import java.util.Date;

import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.DisabledException;
import org.springframework.security.authentication.LockedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.jsonwebtoken.lang.Strings;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import truonggg.dto.request.Auth.SignInRequestDTO;
import truonggg.dto.response.SignInResponse;
import truonggg.dto.response.UserResponseDTO;
import truonggg.exception.NotFoundException;
import truonggg.mapper.UserMapper;
import truonggg.model.User;
import truonggg.repository.UserRepository;
import truonggg.response.SuccessReponse;
import truonggg.sercurity.CustomUserDetails;
import truonggg.service.TokenBlacklistService;
import truonggg.utils.JwtUtils;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

	private final UserMapper userMapper;
	private final AuthenticationManager authenticationManager;
	private final JwtUtils jwtUtils;
	private final UserRepository userRepository;
	private final TokenBlacklistService tokenBlacklistService;

	@PostMapping(path = "/signIn")
	public SuccessReponse<SignInResponse> signIn(@RequestBody @Valid SignInRequestDTO request) {
		try {
			Authentication authentication = authenticationManager.authenticate(
					new UsernamePasswordAuthenticationToken(request.getUserName(), request.getPassword()));

			CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
			User user = userRepository.findByUserName(userDetails.getUsername())
					.orElseThrow(() -> new NotFoundException("user", "User Not Found"));
			if (Boolean.TRUE.equals(user.getIsActive())) {
				throw new AuthenticationException("User account is inactive") {
				};
			}

			String accessToken = jwtUtils.generateToken(userDetails);
			Date expiredDate = jwtUtils.extractExpiration(accessToken);
			UserResponseDTO userDTO = userMapper.toDTO(user);

			return SuccessReponse
					.of(SignInResponse.builder().token(accessToken).expiredDate(expiredDate).user(userDTO).build());

		} catch (BadCredentialsException ex) {
			throw new AuthenticationException("Username or password is incorrect") {
			};
		} catch (DisabledException ex) {
			throw new AuthenticationException("User account is disabled") {
			};
		} catch (LockedException ex) {
			throw new AuthenticationException("User account is locked") {
			};
		}
	}

	@PostMapping(path = "/logout")
	public SuccessReponse<String> logout(HttpServletRequest request) {
		// Lấy token từ request header
		String token = getTokenFromRequest(request);

		if (StringUtils.hasText(token)) {
			// Thêm token vào blacklist để không thể sử dụng lại
			tokenBlacklistService.addToBlacklist(token);
		}

		// Clear SecurityContext
		SecurityContextHolder.clearContext();

		return SuccessReponse.of("Logout successful");
	}

	private String getTokenFromRequest(HttpServletRequest request) {
		String bearerToken = request.getHeader("Authorization");

		if (StringUtils.hasText(bearerToken) && bearerToken.startsWith("Bearer ")) {
			return bearerToken.substring(7);
		}

		return Strings.EMPTY;
	}
}
