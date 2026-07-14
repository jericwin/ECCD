using ECCD.Application.Common.Interfaces;
using Microsoft.Extensions.Logging;

namespace ECCD.Infrastructure.Services;

/// <summary>
/// Email service stub for development. Logs emails to console instead of sending.
/// Replace with MailKit/SendGrid implementation for production.
/// </summary>
public class EmailService : IEmailService
{
    private readonly ILogger<EmailService> _logger;

    public EmailService(ILogger<EmailService> logger)
    {
        _logger = logger;
    }

    public Task SendAsync(string to, string subject, string body, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("=== DEV EMAIL ===\nTo: {To}\nSubject: {Subject}\nBody: {Body}\n=================",
            to, subject, body);
        return Task.CompletedTask;
    }

    public Task SendVerificationCodeAsync(string to, string code, CancellationToken cancellationToken = default)
    {
        return SendAsync(to, "ECCD Verification Code", $"Your verification code is: {code}", cancellationToken);
    }
}
