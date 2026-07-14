namespace ECCD.Application.Common.Interfaces;

/// <summary>
/// JWT token generation service.
/// </summary>
public interface ITokenService
{
    Task<TokenResult> GenerateAccessTokenAsync(string userId, string email, IList<string> roles);
    Task<string> GenerateRefreshTokenAsync(string userId);
    Task<TokenResult?> RefreshAccessTokenAsync(string refreshToken);
}

public class TokenResult
{
    public string AccessToken { get; set; } = string.Empty;
    public string RefreshToken { get; set; } = string.Empty;
    public DateTime ExpiresAt { get; set; }
}
