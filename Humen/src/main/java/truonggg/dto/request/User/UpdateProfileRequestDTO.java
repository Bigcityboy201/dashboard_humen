package truonggg.dto.request.User;

import java.util.Date;

import jakarta.validation.constraints.Email;
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
public class UpdateProfileRequestDTO {

	@Size(max = 100, message = "Full name must be at most 100 characters")
	private String fullName;

	@Email(message = "Email must be valid")
	private String email;

	@Size(max = 20, message = "Phone must be at most 20 characters")
	@Pattern(regexp = "^\\+?\\d{9,15}$", message = "Phone number is invalid")
	private String phone;

	@Size(max = 200, message = "Address must be at most 200 characters")
	private String address;

	@Past(message = "Date of birth must be in the past")
	private Date dateOfBirth;

}

