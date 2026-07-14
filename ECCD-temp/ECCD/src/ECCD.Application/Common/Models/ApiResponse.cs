namespace ECCD.Application.Common.Models;

/// <summary>
/// Standard API response envelope per PRD §11: { data, error, meta }.
/// </summary>
public class ApiResponse<T>
{
    public T? Data { get; set; }
    public ApiError? Error { get; set; }
    public ApiMeta? Meta { get; set; }

    public static ApiResponse<T> Success(T data, ApiMeta? meta = null) => new()
    {
        Data = data,
        Meta = meta
    };

    public static ApiResponse<T> Fail(string code, string message, List<string>? details = null) => new()
    {
        Error = new ApiError { Code = code, Message = message, Details = details ?? new() }
    };
}

public class ApiError
{
    public string Code { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public List<string> Details { get; set; } = new();
}

public class ApiMeta
{
    public int? Page { get; set; }
    public int? PageSize { get; set; }
    public int? TotalCount { get; set; }
    public int? TotalPages { get; set; }
}
