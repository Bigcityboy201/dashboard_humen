package truonggg.dto.request.Role;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Setter
@Getter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class RoleRequestDTO {

	@NotBlank(message = "Role name is required")
	@Size(min = 3, max = 50, message = "Role name must be between 3 and 50 characters")
	private String name;

	@Size(max = 255, message = "Description can be up to 255 characters")
	private String description;
}
