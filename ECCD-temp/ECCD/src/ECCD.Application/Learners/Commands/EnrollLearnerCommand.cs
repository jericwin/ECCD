using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using ECCD.Domain.Entities;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Learners.Commands;

public record EnrollLearnerCommand : IRequest<Result>
{
    public Guid LearnerId { get; init; }
    public Guid ClassroomId { get; init; }
}

public class EnrollLearnerCommandValidator : AbstractValidator<EnrollLearnerCommand>
{
    public EnrollLearnerCommandValidator()
    {
        RuleFor(v => v.LearnerId).NotEmpty();
        RuleFor(v => v.ClassroomId).NotEmpty();
    }
}

public class EnrollLearnerCommandHandler : IRequestHandler<EnrollLearnerCommand, Result>
{
    private readonly IApplicationDbContext _context;

    public EnrollLearnerCommandHandler(IApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Result> Handle(EnrollLearnerCommand request, CancellationToken cancellationToken)
    {
        // 1. Verify classroom exists
        var classroom = await _context.Classrooms
            .Include(c => c.Enrollments)
            .FirstOrDefaultAsync(c => c.Id == request.ClassroomId, cancellationToken);

        if (classroom == null)
        {
            return Result.Failure("Classroom not found.");
        }

        // 2. Verify learner exists
        var learner = await _context.Learners
            .FirstOrDefaultAsync(l => l.Id == request.LearnerId, cancellationToken);

        if (learner == null)
        {
            return Result.Failure("Learner not found.");
        }

        // 3. Verify classroom has not exceeded capacity
        if (classroom.Enrollments.Count >= classroom.MaxLearners)
        {
            return Result.Failure($"Classroom capacity limit of {classroom.MaxLearners} has been reached.");
        }

        // 4. Verify learner is not already enrolled
        var alreadyEnrolled = await _context.ClassroomEnrollments
            .AnyAsync(e => e.ClassroomId == request.ClassroomId && e.LearnerId == request.LearnerId, cancellationToken);

        if (alreadyEnrolled)
        {
            return Result.Failure("Learner is already enrolled in this classroom.");
        }

        var enrollment = new ClassroomEnrollment
        {
            ClassroomId = request.ClassroomId,
            LearnerId = request.LearnerId,
            EnrolledAt = DateTime.UtcNow
        };

        _context.ClassroomEnrollments.Add(enrollment);
        await _context.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }
}
