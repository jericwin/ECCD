using ECCD.Domain.Common;

namespace ECCD.Application.Common.Interfaces;

public interface IIdentityService
{
    Task<(Result result, string userId)> CreateUserAsync(string userName, string email, string password, string role, Guid profileId);
    Task<Result> CheckPasswordAsync(string userNameOrEmail, string password);
    Task<(Result result, string token, string userId, string email, IList<string> roles)> LoginAsync(string userNameOrEmail, string password);
    Task<Result> ResetPasswordAsync(string email, string code, string newPassword);
    Task<string> GeneratePasswordResetCodeAsync(string email);
}
