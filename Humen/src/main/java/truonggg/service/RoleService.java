package truonggg.service;

import java.util.List;

import truonggg.dto.request.Role.RoleRequestDTO;
import truonggg.dto.response.RoleResponseDTO;

public interface RoleService {
	List<RoleResponseDTO> getAll();

	RoleResponseDTO save(final RoleRequestDTO dto);
}
