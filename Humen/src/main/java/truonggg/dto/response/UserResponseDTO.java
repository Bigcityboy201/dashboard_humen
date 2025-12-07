package truonggg.dto.response;

import java.sql.Date;
import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserResponseDTO {
	private Integer id;
	private String fullName;
	private String email;
	private String phone;
	private String userName;
	// private String password;
	private String address;
	private Date dateOfBirth;
	private Date createdAt;
	private boolean active;

	private List<RoleResponseDTO> roles;
}
