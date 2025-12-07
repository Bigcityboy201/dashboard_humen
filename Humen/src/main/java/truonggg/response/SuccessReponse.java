package truonggg.response;

import java.util.Collection;
import java.util.Date;
import java.util.List;
import java.util.Objects;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import truonggg.trace.TraceIdContext;

@Builder
@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class SuccessReponse<T> {
	private final OperationType operationType = OperationType.Success;
	private final String message = "success";
	private ErrorCode code;
	private T data;
	private int size;
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private Integer totalElements;

	@JsonInclude(JsonInclude.Include.NON_NULL)
	private Integer totalPages;

	@JsonInclude(JsonInclude.Include.NON_NULL)
	private Integer page;

	@JsonInclude(JsonInclude.Include.NON_NULL)
	private Integer pageSize;
	private String traceId;
	@JsonFormat(timezone = "Asia/Ho_Chi_Minh", pattern = "dd/MM/yyyy HH:mm:ss")
	@JsonProperty(value = "thời gian")
	private final Date timestamp = new Date();

	// không phân trang
	public static <T> SuccessReponse<T> of(final T data) {
		return SuccessReponse.<T>builder().data(data).code(ErrorCode.OK).size(getSize(data))
				.traceId(TraceIdContext.get()).build();
	}

	// phân trang trả về tổng bản ghi và tổng số trang
	public static <T> SuccessReponse<List<T>> ofPaged(PagedResult<T> paged) {
		return SuccessReponse.<List<T>>builder().data(paged.getContent()).code(ErrorCode.OK)
				.traceId(TraceIdContext.get()).size(paged.getContent() != null ? paged.getContent().size() : 0)
				.page(paged.getCurrentPage()).pageSize(paged.getPageSize()).totalElements(paged.getTotalElements())
				.totalPages(paged.getTotalPages()).build();
	}

	public static <T> int getSize(final T data) {
		if (Objects.nonNull(data) && data instanceof Collection<?>) {
			return ((Collection<?>) data).size();
		}
		return 0;
	}
}
