using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Auth.Commands;

public record LoginCommand : IRequest<Result<LoginResponse>>
{
    public string UsernameOrEmail { get; init; } = string.Empty;
    public string Password { get; init; } = string.Empty;
}

public class LoginCommandValidator : AbstractValidator<LoginCommand>
{
    public LoginCommandValidator()
    {
        RuleFor(v => v.UsernameOrEmail).NotEmpty();
        RuleFor(v => v.Password).NotEmpty();
    }
}

public class LoginCommandHandler : IRequestHandler<LoginCommand, Result<LoginResponse>>
{
    private readonly IIdentityService _identityService;
    private readonly IApplicationDbContext _context;

    public LoginCommandHandler(IIdentityService identityService, IApplicationDbContext context)
    {
        _identityService = identityService;
        _context = context;
    }

    public async Task<Result<LoginResponse>> Handle(LoginCommand request, CancellationToken cancellationToken)
    {
        var (result, token, userId, email, roles) = await _identityService.LoginAsync(
            request.UsernameOrEmail,
            request.Password
        );

        if (!result.IsSuccess)
        {
            return Result<LoginResponse>.Failure(result.Errors);
        }

        var role = roles.FirstOrDefault() ?? "Parent";
        Guid? profileId = null;
        string firstName = "";
        string lastName = "";

        // Retrieve specific profile details based on role
        if (role == "Teacher" || role == "Administrator")
        {
            var teacher = await _context.TeacherProfiles
                .FirstOrDefaultAsync(t => t.UserId == userId, cancellationToken);
            
            if (teacher != null)
            {
                profileId = teacher.Id;
                var names = teacher.FullName.Split(' ');
                firstName = names.FirstOrDefault() ?? "";
                lastName = names.Length > 1 ? string.Join(' ', names.Skip(1)) : "";
            }
        }
        else
        {
            var parent = await _context.ParentProfiles
                .FirstOrDefaultAsync(p => p.UserId == userId, cancellationToken);
            
            if (parent != null)
            {
                profileId = parent.Id;
                var names = parent.FullName.Split(' ');
                firstName = names.FirstOrDefault() ?? "";
                lastName = names.Length > 1 ? string.Join(' ', names.Skip(1)) : "";
            }
        }

        var response = new LoginResponse
        {
            AccessToken = token,
            RefreshToken = "mock-refresh-token", // Refresh token infrastructure is set up as a placeholder
            ExpiresAt = DateTime.UtcNow.AddMinutes(60),
            User = new UserDto
            {
                Id = userId,
                UserName = request.UsernameOrEmail.Contains('@') ? request.UsernameOrEmail.Split('@')[0] : request.UsernameOrEmail,
                Email = email,
                Role = role,
                ProfileId = profileId,
                FirstName = firstName,
                LastName = lastName
            }
        };

        return Result<LoginResponse>.Success(response);
    }
}

public class LoginResponse
{
    public string AccessToken { get; set; } = string.Empty;
    public string RefreshToken { get; set; } = string.Empty;
    public DateTime ExpiresAt { get; set; }
    public UserDto User { get; set; } = null!;
}

public class UserDto
{
    public string Id { get; set; } = string.Empty;
    public string UserName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
    public Guid? ProfileId { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
}
