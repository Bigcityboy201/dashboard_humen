package truonggg.mapper;

import java.util.List;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;

import truonggg.dto.request.User.UserRequestDTO;
import truonggg.dto.response.RoleResponseDTO;
import truonggg.dto.response.UserResponseDTO;
import truonggg.model.User;
import truonggg.model.UserRole;

@Mapper(componentModel = "spring")
public interface UserMapper {

	@Mapping(target = "roles", source = "roles", qualifiedByName = "mapRoles")
	@Mapping(target = "active", source = "isActive")
	UserResponseDTO toDTO(User user);

	@Mapping(target = "roles", ignore = true)
	User toEntity(UserRequestDTO dto);

	// lấy ra role
	@Named("mapRoles")
	default List<RoleResponseDTO> mapRoles(List<UserRole> userRoles) {
		if (userRoles == null)
			return List.of();
		return userRoles.stream().map(ur -> RoleResponseDTO.builder().id(ur.getRole().getId())
				.name(ur.getRole().getName()).description(ur.getRole().getDescription()).build()).toList();
	}

	List<UserResponseDTO> toDTOList(List<User> users);
}
