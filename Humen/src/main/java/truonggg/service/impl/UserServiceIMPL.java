package truonggg.service.impl;

import java.sql.Date;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;
import truonggg.dto.request.User.AdminUpdateUserRequestDTO;
import truonggg.dto.request.User.UpdateProfileRequestDTO;
import truonggg.dto.request.User.UserRequestDTO;
import truonggg.dto.request.User.UserUpdate_Active_RequestDTO;
import truonggg.dto.response.UserResponseDTO;
import truonggg.exception.NotFoundException;
import truonggg.exception.UserAlreadyExistException;
import truonggg.mapper.UserMapper;
import truonggg.model.Role;
import truonggg.model.User;
import truonggg.model.UserRole;
import truonggg.repository.RoleRepository;
import truonggg.repository.UserRepository;
import truonggg.response.PagedResult;
import truonggg.service.UserService;

@Service
@RequiredArgsConstructor
public class UserServiceIMPL implements UserService {

	private final UserRepository userRepository;

	private final UserMapper userMapper;

	private final RoleRepository roleRepository;

	private final PasswordEncoder passwordEncoder;

	@Override
	public PagedResult<UserResponseDTO> getAll(Pageable pageable) {
		Page<User> userPage = this.userRepository.findAll(pageable);
		List<UserResponseDTO> dtoList = userPage.stream().map(userMapper::toDTO).toList();

		return PagedResult.<UserResponseDTO>builder().content(dtoList).totalElements((int) userPage.getTotalElements())
				.totalPages(userPage.getTotalPages()).currentPage(userPage.getNumber()).pageSize(userPage.getSize())
				.build();
	}

	@Override
	public UserResponseDTO save(UserRequestDTO dto) {

		// 1. Check trùng username
		userRepository.findByUserName(dto.getUserName()).ifPresent(u -> {
			throw new UserAlreadyExistException("user", "UserName tồn tại!");
		});

		// 2. Check trùng email
		userRepository.findByEmail(dto.getEmail()).ifPresent(u -> {
			throw new UserAlreadyExistException("user", "Email đã tồn tại!");
		});

		// 3. Map DTO -> Entity
		User user = this.userMapper.toEntity(dto);
		// Encode password bằng BCrypt trước khi lưu
		user.setPassword(passwordEncoder.encode(dto.getPassword()));
		user.setCreatedAt(new Date(System.currentTimeMillis()));

		// 4. Gán role cho user
		if (dto.getRoles() != null && !dto.getRoles().isEmpty()) {
			List<Role> roles = this.roleRepository.findAllById(dto.getRoles());

			List<UserRole> userRoles = roles.stream()
					.map(role -> UserRole.builder().user(user).role(role).assignedAt(LocalDateTime.now()).build())
					.toList();

			user.setRoles(userRoles);
		}

		// 5. Lưu user và trả về DTO
		return this.userMapper.toDTO(this.userRepository.save(user));

	}

	@Override
	public UserResponseDTO updateStatus(Integer id, UserUpdate_Active_RequestDTO dto) {
		User user = this.userRepository.findById(id).orElseThrow(() -> new NotFoundException("User Not Found!"));
		user.setActive(dto.getActive());
		return this.userMapper.toDTO(this.userRepository.save(user));
	}

	@Override
	public Boolean deleteManually(Integer id) {
		User user = this.userRepository.findById(id).orElseThrow(() -> new NotFoundException("User Not Found!"));
		this.userRepository.delete(user);
		return true;
	}

	@Override
	public UserResponseDTO getCurrentUserProfile(String username) {
		User user = this.userRepository.findByUserName(username)
				.orElseThrow(() -> new NotFoundException("user", "User Not Found!"));
		return this.userMapper.toDTO(user);
	}

	@Override
	public UserResponseDTO updateCurrentUserProfile(String username, UpdateProfileRequestDTO dto) {
		User user = this.userRepository.findByUserName(username)
				.orElseThrow(() -> new NotFoundException("user", "User Not Found!"));

		// Kiểm tra email trùng với user khác (nếu có thay đổi email)
		if (dto.getEmail() != null && !dto.getEmail().equals(user.getEmail())) {
			userRepository.findByEmail(dto.getEmail()).ifPresent(u -> {
				if (!u.getId().equals(user.getId())) {
					throw new UserAlreadyExistException("user", "Email đã tồn tại!");
				}
			});
		}

		// Cập nhật các field nếu có giá trị
		if (dto.getFullName() != null) {
			user.setFullName(dto.getFullName());
		}
		if (dto.getEmail() != null) {
			user.setEmail(dto.getEmail());
		}
		if (dto.getPhone() != null) {
			user.setPhone(dto.getPhone());
		}
		if (dto.getAddress() != null) {
			user.setAddress(dto.getAddress());
		}
		if (dto.getDateOfBirth() != null) {
			user.setDateOfBirth(new Date(dto.getDateOfBirth().getTime()));
		}

		return this.userMapper.toDTO(this.userRepository.save(user));
	}

	@Override
	public UserResponseDTO updateUserByAdmin(Integer id, AdminUpdateUserRequestDTO dto) {
		// 1. Tìm user theo id
		User user = this.userRepository.findById(id)
				.orElseThrow(() -> new NotFoundException("user", "User Not Found!"));

		// 2. Kiểm tra email trùng với user khác (nếu có thay đổi email)
		if (dto.getEmail() != null && !dto.getEmail().equals(user.getEmail())) {
			userRepository.findByEmail(dto.getEmail()).ifPresent(u -> {
				if (!u.getId().equals(user.getId())) {
					throw new UserAlreadyExistException("user", "Email đã tồn tại!");
				}
			});
		}

		// 3. Cập nhật các field thông tin nếu có giá trị
		// FullName: cập nhật nếu có giá trị (không null và không rỗng sau khi trim)
		if (dto.getFullName() != null) {
			String trimmedFullName = dto.getFullName().trim();
			if (!trimmedFullName.isEmpty()) {
				user.setFullName(trimmedFullName);
			}
		}
		// Email: cập nhật nếu có giá trị và hợp lệ
		if (dto.getEmail() != null) {
			String trimmedEmail = dto.getEmail().trim();
			if (!trimmedEmail.isEmpty()) {
				user.setEmail(trimmedEmail);
			}
		}
		// Phone: cập nhật nếu có giá trị
		if (dto.getPhone() != null) {
			String trimmedPhone = dto.getPhone().trim();
			if (!trimmedPhone.isEmpty()) {
				user.setPhone(trimmedPhone);
			}
		}
		// Address: cập nhật nếu có giá trị (có thể là empty string để xóa)
		if (dto.getAddress() != null) {
			user.setAddress(dto.getAddress().trim());
		}
		if (dto.getDateOfBirth() != null) {
			user.setDateOfBirth(new java.sql.Date(dto.getDateOfBirth().getTime()));
		}

		// 4. Cập nhật roles nếu có roleIds trong DTO
		if (dto.getRoleIds() != null) {
			// Xóa tất cả roles cũ
			// Với orphanRemoval = true, khi clear() và set lại, JPA sẽ tự động xóa các UserRole cũ khỏi database
			user.getRoles().clear();

			// Thêm roles mới
			if (!dto.getRoleIds().isEmpty()) {
				List<Role> roles = this.roleRepository.findAllById(dto.getRoleIds());
				if (roles.size() != dto.getRoleIds().size()) {
					throw new NotFoundException("role", "Một hoặc nhiều role không tồn tại!");
				}

				// Tạo ArrayList mới thay vì dùng toList() (immutable)
				List<UserRole> userRoles = new ArrayList<>();
				for (Role role : roles) {
					UserRole userRole = UserRole.builder()
							.user(user)
							.role(role)
							.assignedAt(LocalDateTime.now())
							.build();
					userRoles.add(userRole);
				}

				user.setRoles(userRoles);
			} else {
				// Nếu roleIds rỗng, set empty list
				user.setRoles(new ArrayList<>());
			}
		}
		System.out.println("Updating user: " + user.getUserName());
		System.out.println("FullName: " + dto.getFullName());
		System.out.println("Email: " + dto.getEmail());
		System.out.println("Phone: " + dto.getPhone());
		System.out.println("Roles to assign: " + dto.getRoleIds());

		// 5. Lưu và trả về DTO
		return this.userMapper.toDTO(this.userRepository.save(user));
	}

	@Override
	public UserResponseDTO resetPassword(Integer id, String newPassword) {
		User user = this.userRepository.findById(id)
				.orElseThrow(() -> new NotFoundException("user", "User Not Found!"));

		// Encode password mới bằng BCrypt
		user.setPassword(passwordEncoder.encode(newPassword));

		return this.userMapper.toDTO(this.userRepository.save(user));
	}

	@Override
	public UserResponseDTO changePassword(String username, truonggg.dto.request.User.ChangePasswordRequestDTO dto) {
		// 1. Tìm user theo username
		User user = this.userRepository.findByUserName(username)
				.orElseThrow(() -> new NotFoundException("user", "User Not Found!"));

		// 2. Kiểm tra mật khẩu cũ có đúng không
		if (!passwordEncoder.matches(dto.getOldPassword(), user.getPassword())) {
			throw new org.springframework.security.authentication.BadCredentialsException("Old password is incorrect");
		}

		// 3. Kiểm tra mật khẩu mới không được trùng với mật khẩu cũ
		if (passwordEncoder.matches(dto.getNewPassword(), user.getPassword())) {
			throw new IllegalArgumentException("New password must be different from old password");
		}

		// 4. Encode và cập nhật mật khẩu mới
		user.setPassword(passwordEncoder.encode(dto.getNewPassword()));

		// 5. Lưu và trả về DTO
		return this.userMapper.toDTO(this.userRepository.save(user));
	}

}
