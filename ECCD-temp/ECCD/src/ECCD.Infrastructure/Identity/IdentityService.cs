using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Infrastructure.Identity;

public class IdentityService : IIdentityService
{
    private readonly UserManager<ApplicationUser> _userManager;
    private readonly RoleManager<ApplicationRole> _roleManager;
    private readonly ITokenService _tokenService;

    public IdentityService(
        UserManager<ApplicationUser> userManager,
        RoleManager<ApplicationRole> roleManager,
        ITokenService tokenService)
    {
        _userManager = userManager;
        _roleManager = roleManager;
        _tokenService = tokenService;
    }

    public async Task<(Result result, string userId)> CreateUserAsync(string userName, string email, string password, string role, Guid profileId)
    {
        var user = new ApplicationUser
        {
            UserName = userName,
            Email = email,
            ProfileId = profileId,
            IsActive = true
        };

        var result = await _userManager.CreateAsync(user, password);

        if (!result.Succeeded)
        {
            return (Result.Failure(result.Errors.Select(e => e.Description).ToList()), string.Empty);
        }

        // Ensure role exists and add user to role
        if (!await _roleManager.RoleExistsAsync(role))
        {
            await _roleManager.CreateAsync(new ApplicationRole(role));
        }

        var roleResult = await _userManager.AddToRoleAsync(user, role);
        if (!roleResult.Succeeded)
        {
            return (Result.Failure(roleResult.Errors.Select(e => e.Description).ToList()), string.Empty);
        }

        return (Result.Success(), user.Id);
    }

    public async Task<Result> CheckPasswordAsync(string userNameOrEmail, string password)
    {
        var user = await FindUserAsync(userNameOrEmail);
        if (user == null)
        {
            return Result.Failure("Invalid username or password.");
        }

        var isCorrect = await _userManager.CheckPasswordAsync(user, password);
        return isCorrect ? Result.Success() : Result.Failure("Invalid username or password.");
    }

    public async Task<(Result result, string token, string userId, string email, IList<string> roles)> LoginAsync(string userNameOrEmail, string password)
    {
        var user = await FindUserAsync(userNameOrEmail);
        if (user == null)
        {
            return (Result.Failure("User not found."), string.Empty, string.Empty, string.Empty, new List<string>());
        }

        if (!user.IsActive)
        {
            return (Result.Failure("Account is deactivated."), string.Empty, string.Empty, string.Empty, new List<string>());
        }

        var isCorrect = await _userManager.CheckPasswordAsync(user, password);
        if (!isCorrect)
        {
            return (Result.Failure("Invalid username or password."), string.Empty, string.Empty, string.Empty, new List<string>());
        }

        var roles = await _userManager.GetRolesAsync(user);
        var tokenResult = await _tokenService.GenerateAccessTokenAsync(user.Id, user.Email!, roles);

        return (Result.Success(), tokenResult.AccessToken, user.Id, user.Email!, roles);
    }

    public async Task<Result> ResetPasswordAsync(string email, string code, string newPassword)
    {
        var user = await _userManager.FindByEmailAsync(email);
        if (user == null)
        {
            return Result.Failure("User with this email does not exist.");
        }

        // For MVP foundation, since we mock forgot password verification,
        // we'll accept any code or generate a proper reset token internally.
        var token = await _userManager.GeneratePasswordResetTokenAsync(user);
        var result = await _userManager.ResetPasswordAsync(user, token, newPassword);

        return result.Succeeded
            ? Result.Success()
            : Result.Failure(result.Errors.Select(e => e.Description).ToList());
    }

    public async Task<string> GeneratePasswordResetCodeAsync(string email)
    {
        var user = await _userManager.FindByEmailAsync(email);
        if (user == null)
        {
            return string.Empty;
        }

        // Normally we'd generate a 6-digit code. We will use a mock 6-digit code
        // and display it in the logger output.
        var code = new Random().Next(100000, 999999).ToString();
        return code;
    }

    private async Task<ApplicationUser?> FindUserAsync(string userNameOrEmail)
    {
        if (userNameOrEmail.Contains('@'))
        {
            return await _userManager.FindByEmailAsync(userNameOrEmail);
        }
        return await _userManager.FindByNameAsync(userNameOrEmail);
    }
}
