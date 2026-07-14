using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using ECCD.Domain.Enums;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Classrooms.Commands;

public record UpdateClassroomCommand : IRequest<Result>
{
    public Guid Id { get; init; }
    public string Name { get; init; } = string.Empty;
    public SubjectPreset Subject { get; init; }
    public string? Description { get; init; }
    public string? AgeGroup { get; init; }
    public string? SchoolYear { get; init; }
    public string? Schedule { get; init; }
    public string? ThemeColor { get; init; }
    public int MaxLearners { get; init; }
    public ClassroomStatus Status { get; init; }
}

public class UpdateClassroomCommandValidator : AbstractValidator<UpdateClassroomCommand>
{
    public UpdateClassroomCommandValidator()
    {
        RuleFor(v => v.Id).NotEmpty();
        RuleFor(v => v.Name).NotEmpty().MaximumLength(200);
        RuleFor(v => v.Subject).IsInEnum();
        RuleFor(v => v.MaxLearners).GreaterThan(0).LessThanOrEqualTo(100);
        RuleFor(v => v.ThemeColor).MaximumLength(7);
        RuleFor(v => v.Status).IsInEnum();
    }
}

public class UpdateClassroomCommandHandler : IRequestHandler<UpdateClassroomCommand, Result>
{
    private readonly IApplicationDbContext _context;
    private readonly ICurrentUserService _currentUserService;

    public UpdateClassroomCommandHandler(IApplicationDbContext context, ICurrentUserService currentUserService)
    {
        _context = context;
        _currentUserService = currentUserService;
    }

    public async Task<Result> Handle(UpdateClassroomCommand request, CancellationToken cancellationToken)
    {
        var classroom = await _context.Classrooms
            .FirstOrDefaultAsync(c => c.Id == request.Id, cancellationToken);

        if (classroom == null)
        {
            return Result.Failure("Classroom not found.");
        }

        // Verify ownership (the teacher who created the classroom)
        var userId = _currentUserService.UserId;
        var teacher = await _context.TeacherProfiles
            .FirstOrDefaultAsync(t => t.UserId == userId, cancellationToken);

        if (teacher == null || classroom.TeacherId != teacher.Id)
        {
            return Result.Failure("You do not have permission to modify this classroom.");
        }

        classroom.Name = request.Name;
        classroom.Subject = request.Subject;
        classroom.Description = request.Description;
        classroom.AgeGroup = request.AgeGroup;
        classroom.SchoolYear = request.SchoolYear;
        classroom.Schedule = request.Schedule;
        classroom.ThemeColor = request.ThemeColor;
        classroom.MaxLearners = request.MaxLearners;
        classroom.Status = request.Status;

        await _context.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }
}
