package truonggg.sercurity;

import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import truonggg.model.User;
import truonggg.repository.UserRepository;

@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {
	private final UserRepository userRepository;

	@Override
	@Transactional
	public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
		System.out.println("Trying to load user: " + username);

		User user = this.userRepository.findByUserName(username).orElseThrow(() -> {
			System.out.println("User not found: " + username);
			return new UsernameNotFoundException("Cannot find user with userName: " + username);
		});

		System.out.println("User found: " + user.getUserName() + ", password hash: " + user.getPassword());
		return new CustomUserDetails(user);
	}
}
