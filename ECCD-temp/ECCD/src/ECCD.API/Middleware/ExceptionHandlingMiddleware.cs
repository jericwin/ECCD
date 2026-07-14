using System.Net;
using System.Text.Json;
using ECCD.Application.Common.Exceptions;
using ECCD.Application.Common.Models;

namespace ECCD.API.Middleware;

/// <summary>
/// Global exception handler — catches all unhandled exceptions and returns
/// the standard { data, error, meta } envelope per PRD §11.
/// </summary>
public class ExceptionHandlingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionHandlingMiddleware> _logger;

    public ExceptionHandlingMiddleware(RequestDelegate next, ILogger<ExceptionHandlingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        var (statusCode, code, message, details) = exception switch
        {
            ValidationException validationEx => (
                HttpStatusCode.BadRequest,
                "VALIDATION_ERROR",
                "One or more validation errors occurred.",
                validationEx.Errors.SelectMany(e => e.Value.Select(v => $"{e.Key}: {v}")).ToList()
            ),
            NotFoundException notFoundEx => (
                HttpStatusCode.NotFound,
                "NOT_FOUND",
                notFoundEx.Message,
                new List<string>()
            ),
            ForbiddenAccessException forbiddenEx => (
                HttpStatusCode.Forbidden,
                "FORBIDDEN",
                forbiddenEx.Message,
                new List<string>()
            ),
            UnauthorizedAccessException => (
                HttpStatusCode.Unauthorized,
                "UNAUTHORIZED",
                "You are not authorized to perform this action.",
                new List<string>()
            ),
            _ => (
                HttpStatusCode.InternalServerError,
                "INTERNAL_ERROR",
                "An unexpected error occurred.",
                new List<string>()
            )
        };

        if (statusCode == HttpStatusCode.InternalServerError)
        {
            _logger.LogError(exception, "Unhandled exception: {Message}", exception.Message);
        }
        else
        {
            _logger.LogWarning("Handled exception [{Code}]: {Message}", code, message);
        }

        context.Response.ContentType = "application/json";
        context.Response.StatusCode = (int)statusCode;

        var response = ApiResponse<object>.Fail(code, message, details);
        var json = JsonSerializer.Serialize(response, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        await context.Response.WriteAsync(json);
    }
}
