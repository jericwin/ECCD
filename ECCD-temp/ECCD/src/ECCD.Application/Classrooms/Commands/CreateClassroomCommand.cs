using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using ECCD.Domain.Entities;
using ECCD.Domain.Enums;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Classrooms.Commands;

public record CreateClassroomCommand : IRequest<Result<Guid>>
{
    public string Name { get; init; } = string.Empty;
    public SubjectPreset Subject { get; init; }
    public string? Description { get; init; }
    public string? AgeGroup { get; init; }
    public string? SchoolYear { get; init; }
    public string? Schedule { get; init; }
    public string? ThemeColor { get; init; }
    public int MaxLearners { get; init; } = 30;
}

public class CreateClassroomCommandValidator : AbstractValidator<CreateClassroomCommand>
{
    public CreateClassroomCommandValidator()
    {
        RuleFor(v => v.Name).NotEmpty().MaximumLength(200);
        RuleFor(v => v.Subject).IsInEnum();
        RuleFor(v => v.MaxLearners).GreaterThan(0).LessThanOrEqualTo(100);
        RuleFor(v => v.ThemeColor).MaximumLength(7); // #RRGGBB
    }
}

public class CreateClassroomCommandHandler : IRequestHandler<CreateClassroomCommand, Result<Guid>>
{
    private readonly IApplicationDbContext _context;
    private readonly ICurrentUserService _currentUserService;

    public CreateClassroomCommandHandler(IApplicationDbContext context, ICurrentUserService currentUserService)
    {
        _context = context;
        _currentUserService = currentUserService;
    }

    public async Task<Result<Guid>> Handle(CreateClassroomCommand request, CancellationToken cancellationToken)
    {
        var userId = _currentUserService.UserId;
        if (string.IsNullOrEmpty(userId))
        {
            return Result<Guid>.Failure("Unauthorized access.");
        }

        // Fetch the corresponding TeacherProfile
        var teacher = await _context.TeacherProfiles
            .FirstOrDefaultAsync(t => t.UserId == userId, cancellationToken);

        if (teacher == null)
        {
            return Result<Guid>.Failure("User is not registered as a teacher.");
        }

        var classroom = new Classroom
        {
            Name = request.Name,
            Subject = request.Subject,
            Description = request.Description,
            AgeGroup = request.AgeGroup,
            SchoolYear = request.SchoolYear,
            Schedule = request.Schedule,
            ThemeColor = request.ThemeColor,
            MaxLearners = request.MaxLearners,
            TeacherId = teacher.Id,
            CdcId = teacher.CdcId,
            Status = ClassroomStatus.Active // Default to active for MVP usability
        };

        _context.Classrooms.Add(classroom);
        await _context.SaveChangesAsync(cancellationToken);

        // Auto-create standard subject folders (Mathematics, English, Mother Tongue, etc.) per PRD FR-5.2
        var folders = Enum.GetValues<SubjectPreset>().Select(sp => new ClassworkFolder
        {
            ClassroomId = classroom.Id,
            Subject = sp
        });
        _context.ClassworkFolders.AddRange(folders);
        await _context.SaveChangesAsync(cancellationToken);

        return Result<Guid>.Success(classroom.Id);
    }
}
