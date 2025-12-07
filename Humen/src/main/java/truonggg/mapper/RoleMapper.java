package truonggg.mapper;

import java.util.List;

import org.mapstruct.Mapper;

import truonggg.dto.request.Role.RoleRequestDTO;
import truonggg.dto.response.RoleResponseDTO;
import truonggg.model.Role;

@Mapper(componentModel = "spring")
public interface RoleMapper {

	RoleResponseDTO toDTO(final Role role);

	List<RoleResponseDTO> toDTOList(final List<Role> role);

	Role toModel(final RoleRequestDTO dto);
}
