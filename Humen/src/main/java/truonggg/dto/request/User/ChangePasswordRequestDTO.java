package truonggg.dto.request.User;

import jakarta.validation.constraints.NotBlank;
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
public class ChangePasswordRequestDTO {

	@NotBlank(message = "Old password is required")
	private String oldPassword;

	@NotBlank(message = "New password is required")
	@Size(min = 6, max = 50, message = "Password must be between 6 and 50 characters")
	@Pattern(regexp = "^(?=.*[A-Z])(?=.*\\d).+$", message = "Password must contain at least one uppercase letter and one number")
	private String newPassword;
}








