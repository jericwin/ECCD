using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using ECCD.Domain.Entities;
using ECCD.Domain.Enums;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Learners.Commands;

public record RegisterLearnerCommand : IRequest<Result<Guid>>
{
    public string FirstName { get; init; } = string.Empty;
    public string LastName { get; init; } = string.Empty;
    public string? PhotoUrl { get; init; }
    public DateTime Birthdate { get; init; }
    public Gender Gender { get; init; }
    public string LearnerIdCode { get; init; } = string.Empty; // LRN code
    public Guid ParentId { get; init; }
    public Guid CdcId { get; init; }
}

public class RegisterLearnerCommandValidator : AbstractValidator<RegisterLearnerCommand>
{
    public RegisterLearnerCommandValidator()
    {
        RuleFor(v => v.FirstName).NotEmpty().MaximumLength(100);
        RuleFor(v => v.LastName).NotEmpty().MaximumLength(100);
        RuleFor(v => v.Birthdate).NotEmpty().LessThan(DateTime.UtcNow.AddYears(-2)).WithMessage("Learner must be at least 2 years old.");
        RuleFor(v => v.Gender).IsInEnum();
        RuleFor(v => v.LearnerIdCode).NotEmpty().MaximumLength(50);
        RuleFor(v => v.ParentId).NotEmpty();
        RuleFor(v => v.CdcId).NotEmpty();
    }
}

public class RegisterLearnerCommandHandler : IRequestHandler<RegisterLearnerCommand, Result<Guid>>
{
    private readonly IApplicationDbContext _context;

    public RegisterLearnerCommandHandler(IApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Result<Guid>> Handle(RegisterLearnerCommand request, CancellationToken cancellationToken)
    {
        // Check for duplicate LearnerIdCode (LRN) (PRD FR-1.7)
        var duplicate = await _context.Learners
            .IgnoreQueryFilters() // check even deleted ones to avoid unique index violation in MySQL
            .AnyAsync(l => l.LearnerIdCode == request.LearnerIdCode, cancellationToken);

        if (duplicate)
        {
            return Result<Guid>.Failure($"Learner ID code '{request.LearnerIdCode}' is already registered.");
        }

        // Verify parent exists
        var parentExists = await _context.ParentProfiles
            .AnyAsync(p => p.Id == request.ParentId, cancellationToken);
        if (!parentExists)
        {
            return Result<Guid>.Failure("Linked Parent profile does not exist.");
        }

        // Verify CDC exists
        var cdcExists = await _context.ChildDevelopmentCenters
            .AnyAsync(c => c.Id == request.CdcId, cancellationToken);
        if (!cdcExists)
        {
            return Result<Guid>.Failure("Linked CDC does not exist.");
        }

        var learner = new Learner
        {
            FirstName = request.FirstName,
            LastName = request.LastName,
            PhotoUrl = request.PhotoUrl,
            Birthdate = request.Birthdate,
            Gender = request.Gender,
            LearnerIdCode = request.LearnerIdCode,
            ParentId = request.ParentId,
            CdcId = request.CdcId
        };

        _context.Learners.Add(learner);
        await _context.SaveChangesAsync(cancellationToken);

        return Result<Guid>.Success(learner.Id);
    }
}
