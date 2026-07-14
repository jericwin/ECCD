using MediatR;
using Microsoft.Extensions.Logging;
using System.Diagnostics;

namespace ECCD.Application.Common.Behaviors;

/// <summary>
/// MediatR pipeline behavior that logs request/response with timing.
/// Warns on slow requests (> 500ms).
/// </summary>
public class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : notnull
{
    private readonly ILogger<LoggingBehavior<TRequest, TResponse>> _logger;

    public LoggingBehavior(ILogger<LoggingBehavior<TRequest, TResponse>> logger)
    {
        _logger = logger;
    }

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken cancellationToken)
    {
        var requestName = typeof(TRequest).Name;

        _logger.LogInformation("ECCD Request: {Name} {@Request}", requestName, request);

        var stopwatch = Stopwatch.StartNew();
        var response = await next();
        stopwatch.Stop();

        var elapsedMs = stopwatch.ElapsedMilliseconds;

        if (elapsedMs > 500)
        {
            _logger.LogWarning("ECCD Long Running Request: {Name} ({ElapsedMs} ms) {@Request}",
                requestName, elapsedMs, request);
        }
        else
        {
            _logger.LogInformation("ECCD Request Completed: {Name} ({ElapsedMs} ms)", requestName, elapsedMs);
        }

        return response;
    }
}
