package truonggg.dto.request.Auth;

import jakarta.validation.constraints.NotBlank;
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
public class SignInRequestDTO {
	@NotBlank(message = "Username không được để trống")
	private String userName;

	@NotBlank(message = "Password không được để trống")
	private String password;
}
