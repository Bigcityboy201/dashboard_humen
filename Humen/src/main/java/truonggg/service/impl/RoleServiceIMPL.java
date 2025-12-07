package truonggg.service.impl;

import java.util.List;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;
import truonggg.dto.request.Role.RoleRequestDTO;
import truonggg.dto.response.RoleResponseDTO;
import truonggg.mapper.RoleMapper;
import truonggg.model.Role;
import truonggg.repository.RoleRepository;
import truonggg.service.RoleService;

@Service
@RequiredArgsConstructor
public class RoleServiceIMPL implements RoleService {

	private final RoleRepository roleRepository;
	private final RoleMapper roleMapper;

	@Override
	public List<RoleResponseDTO> getAll() {
		return this.roleMapper.toDTOList(this.roleRepository.findAll());
	}

	@Override
	public RoleResponseDTO save(final RoleRequestDTO dto) {
		Role role = this.roleMapper.toModel(dto);
		Role savedRole = this.roleRepository.save(role);
		return this.roleMapper.toDTO(savedRole);
	}

}
