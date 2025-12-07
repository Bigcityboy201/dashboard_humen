package truonggg.service.impl;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Service;

import truonggg.service.TokenBlacklistService;

@Service
public class TokenBlacklistServiceIMPL implements TokenBlacklistService {

	// Sử dụng ConcurrentHashMap để thread-safe
	// Có thể nâng cấp lên Redis sau nếu cần
	private final Set<String> blacklistedTokens = ConcurrentHashMap.newKeySet();

	@Override
	public void addToBlacklist(String token) {
		if (token != null && !token.isEmpty()) {
			blacklistedTokens.add(token);
		}
	}

	@Override
	public boolean isBlacklisted(String token) {
		return token != null && blacklistedTokens.contains(token);
	}
}

