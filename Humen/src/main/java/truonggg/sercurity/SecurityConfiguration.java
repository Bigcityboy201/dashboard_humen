package truonggg.sercurity;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Lazy;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfiguration {

	private static final String[] WHITE_LIST = { "/auth/**" };

	private final JwtAuthenticationFilter jwtRequestFilter;
	private final UserDetailsService userDetailsService;
	private final CustomAccessDeniedHandler accessDeniedHandler;
	private final CustomAuthenticationEntryPoint authenticationEntryPoint;

	@Lazy
	public SecurityConfiguration(JwtAuthenticationFilter jwtRequestFilter, UserDetailsService userDetailsService,
			CustomAccessDeniedHandler accessDeniedHandler, CustomAuthenticationEntryPoint authenticationEntryPoint) {
		this.jwtRequestFilter = jwtRequestFilter;
		this.userDetailsService = userDetailsService;
		this.accessDeniedHandler = accessDeniedHandler;
		this.authenticationEntryPoint = authenticationEntryPoint;
	}

	@Bean
	AuthenticationManager authenticationManager(AuthenticationConfiguration authConfiguration) throws Exception {
		return authConfiguration.getAuthenticationManager();
	}

	@Bean
	PasswordEncoder passwordEncoder() {
		return new BCryptPasswordEncoder(); // salt
	}

	@Bean
	AuthenticationProvider authenticationProvider() {
		DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider();
		authProvider.setUserDetailsService(this.userDetailsService);
		authProvider.setPasswordEncoder(this.passwordEncoder());

		return authProvider;
	}

	@Bean
	CorsConfigurationSource corsConfigurationSource() {
		CorsConfiguration configuration = new CorsConfiguration();
		configuration.addAllowedOriginPattern("*");
		configuration.addAllowedMethod("*");
		configuration.addAllowedHeader("*");
		configuration.setAllowCredentials(true);

		UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
		source.registerCorsConfiguration("/**", configuration);
		return source;
	}

	@Bean
	SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
		http.csrf(AbstractHttpConfigurer::disable);
		http.cors(cors -> cors.configurationSource(corsConfigurationSource()));

		http.authorizeHttpRequests(auths -> auths
				// Public endpoints - không cần xác thực
				.requestMatchers(WHITE_LIST).permitAll()

				// UserController - chỉ ADMIN
				.requestMatchers("/users/**").hasRole("ADMIN")

				// ProfileController - HR_MANAGER hoặc ADMIN (được xử lý bởi @PreAuthorize)
				.requestMatchers("/profile/**").hasAnyRole("ADMIN", "HR_MANAGER", "PAYROLL_MANAGER")

				// ========== API Python - Payment (PAYROLL_MANAGER hoặc ADMIN) ==========
				// Salaries endpoints
				.requestMatchers("/api/python/salaries/**").hasAnyRole("ADMIN", "PAYROLL_MANAGER")
				// Dividends endpoints
				.requestMatchers("/api/python/dividends/**").hasAnyRole("ADMIN", "PAYROLL_MANAGER")

				// ========== API Python - HR Management (HR_MANAGER hoặc ADMIN) ==========
				// Employees endpoints: GET /employees, POST /employees, GET/PUT/DELETE
				// /employees/{id}
				.requestMatchers("/api/python/employees/**").hasAnyRole("ADMIN", "HR_MANAGER")
				// Attendance endpoints: GET /attendance, POST /attendance, GET/PUT/DELETE
				// /attendance/{id}, GET /attendance/statistics
				.requestMatchers("/api/python/attendance/**").hasAnyRole("ADMIN", "HR_MANAGER")
				// Departments endpoints: GET /departments, POST /departments, GET/PUT/DELETE
				// /departments/{id}, GET /departments/{id}/employees
				.requestMatchers("/api/python/departments/**").hasAnyRole("ADMIN", "HR_MANAGER")
				// Positions endpoints: GET /positions, POST /positions, GET/PUT/DELETE
				// /positions/{id}, GET /positions/{id}/employees
				.requestMatchers("/api/python/positions/**").hasAnyRole("ADMIN", "HR_MANAGER")
				// Dashboard endpoints: GET /dashboard/overview (cho HR_MANAGER, PAYROLL_MANAGER và ADMIN)
				.requestMatchers("/api/python/dashboard/**").hasAnyRole("ADMIN", "HR_MANAGER", "PAYROLL_MANAGER")
				// Reports endpoints: GET /reports/** (cho PAYROLL_MANAGER và ADMIN để xem báo cáo tài chính)
				.requestMatchers("/api/python/reports/**").hasAnyRole("ADMIN", "PAYROLL_MANAGER")

				// API Python - Tất cả endpoint khác - chỉ ADMIN
				.requestMatchers("/api/python/**").hasRole("ADMIN")

				// Health check - public
				.requestMatchers("/api/v1/health").permitAll()

				// Tất cả request khác cần xác thực
				.anyRequest().authenticated())
				.sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
				.authenticationProvider(this.authenticationProvider())
				.addFilterBefore(this.jwtRequestFilter, UsernamePasswordAuthenticationFilter.class)
				.exceptionHandling(handler -> handler.accessDeniedHandler(this.accessDeniedHandler)
						.authenticationEntryPoint(this.authenticationEntryPoint));
		return http.build();
	}
}