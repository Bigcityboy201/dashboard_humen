package truonggg.response;

import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@Builder
public class PagedResult<T> {
	private List<T> content;
	private int totalElements;
	private int totalPages;
	private int currentPage;
	private int pageSize;
}
