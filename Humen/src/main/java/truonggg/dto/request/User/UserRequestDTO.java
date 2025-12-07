package truonggg.dto.request.User;

import java.util.Date;
import java.util.List;

import jakarta.persistence.Column;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Past;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserRequestDTO {

	@Size(max = 100, message = "Full name must be at most 100 characters")
	@NotBlank(message = "FullName is required")
	private String fullName;

	@NotBlank(message = "Email is required")
	@Email(message = "Email must be valid")
	@Column(nullable = false, unique = true)
	private String email;

	@NotBlank(message = "Phone is required")
	@Size(max = 20, message = "Phone must be at most 20 characters")
	@Pattern(regexp = "^\\+?\\d{9,15}$", message = "Phone number is invalid")
	private String phone;

	@NotBlank(message = "Username is required")
	@Size(max = 50, message = "Username must be at most 50 characters")
	@Pattern(regexp = "^[\\S]+$", message = "Username must not contain spaces")
	private String userName;

	@NotBlank(message = "Password is required")
	@Size(min = 6, max = 50, message = "Password must be between 6 and 50 characters")
	@Pattern(regexp = "^(?=.*[A-Z])(?=.*\\d).+$", message = "Password must contain at least one uppercase letter and one number")
	private String password;

	@Size(max = 200, message = "Address must be at most 200 characters")
	private String address;

	@NotNull(message = "Date of birth is required")
	@Past(message = "Date of birth must be in the past")
	private Date dateOfBirth;

	@NotEmpty(message = "At least one role must be assigned")
	private List<Integer> roles;

}
