namespace ECCD.Application.Common.Interfaces;

/// <summary>
/// Retrieves the currently authenticated user's info from HttpContext claims.
/// </summary>
public interface ICurrentUserService
{
    string? UserId { get; }
    string? UserName { get; }
    string? Email { get; }
    IEnumerable<string> Roles { get; }
    bool IsAuthenticated { get; }
    bool IsInRole(string role);
}
