package truonggg.sercurity;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import lombok.Getter;
import lombok.Setter;
import truonggg.model.Role;
import truonggg.model.User;
import truonggg.model.UserRole;

@Getter
@Setter
public class CustomUserDetails implements UserDetails {
	private static final long serialVersionUID = 1L;
	private final String userName;
	private final String password;
	private final Set<GrantedAuthority> authorities;
	private final Set<Role> roles;
	private final boolean isActive;

	public CustomUserDetails(final User user) {
		this.userName = user.getUserName();
		this.password = user.getPassword();
		this.isActive = !user.getIsActive(); // Logic: isActive = 0 (false) = đang hoạt động, isActive = 1 (true) =
												// ngưng

		// Lấy roles từ User.roles (List<UserRole>)
		Set<GrantedAuthority> authSet = new HashSet<>();
		Set<Role> roleSet = new HashSet<>();

		if (user.getRoles() != null && !user.getRoles().isEmpty()) {
			for (UserRole userRole : user.getRoles()) {
				Role role = userRole.getRole();
				if (role != null) {
					roleSet.add(role);
					// Tạo authority từ role name với prefix ROLE_
					authSet.add(new SimpleGrantedAuthority("ROLE_" + role.getName()));
				}
			}
		} else {
			System.out.println("WARNING: User " + this.userName + " has no role assigned!");
		}

		this.authorities = authSet;
		this.roles = roleSet;

	}

	@Override
	public Collection<? extends GrantedAuthority> getAuthorities() {
		return this.authorities;
	}

	@Override
	public String getPassword() {
		return this.password;
	}

	@Override
	public String getUsername() {
		return this.userName;
	}

	@Override
	public boolean isAccountNonExpired() {
		return true;
	}

	@Override
	public boolean isAccountNonLocked() {
		return true;
	}

	@Override
	public boolean isCredentialsNonExpired() {
		return true;
	}

	@Override
	public boolean isEnabled() {
		return this.isActive;
	}
}
