using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using FluentValidation;
using MediatR;

namespace ECCD.Application.Auth.Commands;

public record ForgotPasswordCommand : IRequest<Result>
{
    public string Email { get; init; } = string.Empty;
}

public class ForgotPasswordCommandValidator : AbstractValidator<ForgotPasswordCommand>
{
    public ForgotPasswordCommandValidator()
    {
        RuleFor(v => v.Email).NotEmpty().EmailAddress();
    }
}

public class ForgotPasswordCommandHandler : IRequestHandler<ForgotPasswordCommand, Result>
{
    private readonly IIdentityService _identityService;
    private readonly IEmailService _emailService;

    public ForgotPasswordCommandHandler(IIdentityService identityService, IEmailService emailService)
    {
        _identityService = identityService;
        _emailService = emailService;
    }

    public async Task<Result> Handle(ForgotPasswordCommand request, CancellationToken cancellationToken)
    {
        var code = await _identityService.GeneratePasswordResetCodeAsync(request.Email);
        
        if (string.IsNullOrEmpty(code))
        {
            // For privacy safety, we don't disclose if email doesn't exist
            return Result.Success();
        }

        // Send code via email service (stubbed out to console in dev)
        await _emailService.SendVerificationCodeAsync(request.Email, code, cancellationToken);

        return Result.Success();
    }
}
