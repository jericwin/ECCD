using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using ECCD.Domain.Entities;
using ECCD.Domain.Enums;
using FluentValidation;
using MediatR;

namespace ECCD.Application.Auth.Commands;

public record RegisterParentCommand : IRequest<Result<string>>
{
    public string UserName { get; init; } = string.Empty;
    public string Email { get; init; } = string.Empty;
    public string Password { get; init; } = string.Empty;
    public string FullName { get; init; } = string.Empty;
    public string RelationshipToLearner { get; init; } = string.Empty;
    public string? Mobile { get; init; }
    public string? Address { get; init; }
    public bool ConsentedToToS { get; init; }
    public string? IpAddress { get; init; }
    public string? UserAgent { get; init; }
}

public class RegisterParentCommandValidator : AbstractValidator<RegisterParentCommand>
{
    public RegisterParentCommandValidator()
    {
        RuleFor(v => v.UserName).NotEmpty().MaximumLength(50);
        RuleFor(v => v.Email).NotEmpty().EmailAddress();
        RuleFor(v => v.Password).NotEmpty().MinimumLength(8);
        RuleFor(v => v.FullName).NotEmpty().MaximumLength(200);
        RuleFor(v => v.RelationshipToLearner).NotEmpty().MaximumLength(50);
        RuleFor(v => v.ConsentedToToS).Equal(true).WithMessage("You must consent to the Terms of Service and Privacy Policy.");
    }
}

public class RegisterParentCommandHandler : IRequestHandler<RegisterParentCommand, Result<string>>
{
    private readonly IApplicationDbContext _context;
    private readonly IIdentityService _identityService;

    public RegisterParentCommandHandler(IApplicationDbContext context, IIdentityService identityService)
    {
        _context = context;
        _identityService = identityService;
    }

    public async Task<Result<string>> Handle(RegisterParentCommand request, CancellationToken cancellationToken)
    {
        // 1. Create ParentProfile
        var profile = new ParentProfile
        {
            FullName = request.FullName,
            RelationshipToLearner = request.RelationshipToLearner,
            Mobile = request.Mobile,
            Address = request.Address
        };

        _context.ParentProfiles.Add(profile);

        // 2. Register Identity User linked to profile
        var (identityResult, userId) = await _identityService.CreateUserAsync(
            request.UserName,
            request.Email,
            request.Password,
            UserRole.Parent.ToString(),
            profile.Id
        );

        if (!identityResult.IsSuccess)
        {
            return Result<string>.Failure(identityResult.Errors);
        }

        // Link profile to user
        profile.UserId = userId;
        await _context.SaveChangesAsync(cancellationToken);

        // 3. Log Consent record for DPA compliance (PRD §8.2)
        var consent = new ConsentRecord
        {
            UserId = userId,
            ConsentType = "ToS_PrivacyPolicy",
            ConsentedAt = DateTime.UtcNow,
            IpAddress = request.IpAddress,
            UserAgent = request.UserAgent
        };
        _context.ConsentRecords.Add(consent);
        await _context.SaveChangesAsync(cancellationToken);

        return Result<string>.Success(userId);
    }
}
