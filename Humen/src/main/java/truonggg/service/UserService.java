package truonggg.service;

import org.springframework.data.domain.Pageable;

import truonggg.dto.request.User.UpdateProfileRequestDTO;
import truonggg.dto.request.User.UserRequestDTO;
import truonggg.dto.request.User.UserUpdate_Active_RequestDTO;
import truonggg.dto.response.UserResponseDTO;
import truonggg.response.PagedResult;

public interface UserService {

	PagedResult<UserResponseDTO> getAll(Pageable pageable);

	UserResponseDTO save(UserRequestDTO dto);

	UserResponseDTO updateStatus(final Integer id, final UserUpdate_Active_RequestDTO dto);

	Boolean deleteManually(final Integer id);

	UserResponseDTO getCurrentUserProfile(String username);

	UserResponseDTO updateCurrentUserProfile(String username, UpdateProfileRequestDTO dto);

	UserResponseDTO updateUserByAdmin(Integer id, truonggg.dto.request.User.AdminUpdateUserRequestDTO dto);

	UserResponseDTO resetPassword(Integer id, String newPassword);

	UserResponseDTO changePassword(String username, truonggg.dto.request.User.ChangePasswordRequestDTO dto);
}
