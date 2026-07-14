namespace ECCD.Application.Common.Interfaces;

/// <summary>
/// Email service for sending verification codes and notifications.
/// </summary>
public interface IEmailService
{
    Task SendAsync(string to, string subject, string body, CancellationToken cancellationToken = default);
    Task SendVerificationCodeAsync(string to, string code, CancellationToken cancellationToken = default);
}
