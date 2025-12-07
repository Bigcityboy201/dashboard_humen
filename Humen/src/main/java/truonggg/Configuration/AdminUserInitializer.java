package truonggg.Configuration;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import lombok.RequiredArgsConstructor;
import truonggg.constant.SecurityRole;
import truonggg.model.Role;
import truonggg.model.User;
import truonggg.model.UserRole;
import truonggg.repository.RoleRepository;
import truonggg.repository.UserRepository;

@Component
@RequiredArgsConstructor
public class AdminUserInitializer implements CommandLineRunner {

	private final RoleRepository roleRepository;
	private final UserRepository userRepository;
	private final PasswordEncoder passwordEncoder;

	@Value("${admin.default.username:quangtruongngo2012004}")
	private String adminUsername;

	@Value("${admin.default.password:quangtruong1}")
	private String adminPassword;

	@Value("${admin.default.email:quangtruong2012004@gmail.com}")
	private String adminEmail;

	@Override
	public void run(String... args) throws Exception {
		// 1. Tạo role cơ bản nếu chưa có
		createBasicRolesIfNotExists();

		// 2. Tạo admin user lần đầu, inactive
		createAdminUserIfNotExists();
	}

	private void createBasicRolesIfNotExists() {
		createRoleIfNotExists(SecurityRole.ROLE_ADMIN, "Administrator role");
		createRoleIfNotExists(SecurityRole.ROLE_HR, "Regular user role");
		createRoleIfNotExists(SecurityRole.ROLE_PAYROLL, "Employee role");
	}

	private void createRoleIfNotExists(String roleName, String description) {
		Role role = roleRepository.findByName(roleName).orElse(null);
		if (role == null) {
			role = Role.builder().name(roleName).description(description).build();
			roleRepository.save(role);
			System.out.println("Created role: " + roleName);
		} else {
			System.out.println("Role already exists: " + roleName);
		}
	}

	private void createAdminUserIfNotExists() {
		User admin = userRepository.findByUserName(adminUsername).orElse(null);

		if (admin == null) {
			// Lấy role ADMIN trước khi tạo user
			Role adminRole = roleRepository.findByName(SecurityRole.ROLE_ADMIN).orElse(null);

			if (adminRole == null) {
				System.out.println("ERROR: ADMIN role not found! Please create roles first.");
				return;
			}

			// Tạo user admin inactive
			admin = User.builder().userName(adminUsername).password(passwordEncoder.encode(adminPassword))
					.fullName("Quang Truong").email(adminEmail).phone("0123456789").isActive(false)
					.roles(new ArrayList<>()).build();

			// Tạo UserRole để liên kết User và Role
			UserRole userRole = UserRole.builder().user(admin).role(adminRole)
					.assignedAt(LocalDateTime.now()).build();

			// Gán UserRole vào User
			List<UserRole> userRoles = new ArrayList<>();
			userRoles.add(userRole);
			admin.setRoles(userRoles);

			admin = userRepository.save(admin);
			System.out.println("Created admin user: " + adminUsername + " isActive=false with role_id="
					+ adminRole.getId());
		} else {
			// Kiểm tra và cập nhật role nếu chưa có
			if (admin.getRoles() == null || admin.getRoles().isEmpty()) {
				Role adminRole = roleRepository.findByName(SecurityRole.ROLE_ADMIN).orElse(null);
				if (adminRole != null) {
					UserRole userRole = UserRole.builder().user(admin).role(adminRole)
							.assignedAt(LocalDateTime.now()).build();
					List<UserRole> userRoles = new ArrayList<>();
					userRoles.add(userRole);
					admin.setRoles(userRoles);
					userRepository.save(admin);
					System.out.println("Updated admin user: set role_id=" + adminRole.getId());
				}
			} else {
				System.out.println("Admin user already exists with roles, nothing changed");
			}
		}
	}
}
