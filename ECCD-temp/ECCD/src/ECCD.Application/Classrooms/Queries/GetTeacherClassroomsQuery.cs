using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using ECCD.Domain.Enums;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Classrooms.Queries;

public record GetTeacherClassroomsQuery : IRequest<Result<List<ClassroomDto>>>;

public class GetTeacherClassroomsQueryHandler : IRequestHandler<GetTeacherClassroomsQuery, Result<List<ClassroomDto>>>
{
    private readonly IApplicationDbContext _context;
    private readonly ICurrentUserService _currentUserService;

    public GetTeacherClassroomsQueryHandler(IApplicationDbContext context, ICurrentUserService currentUserService)
    {
        _context = context;
        _currentUserService = currentUserService;
    }

    public async Task<Result<List<ClassroomDto>>> Handle(GetTeacherClassroomsQuery request, CancellationToken cancellationToken)
    {
        var userId = _currentUserService.UserId;
        if (string.IsNullOrEmpty(userId))
        {
            return Result<List<ClassroomDto>>.Failure("Unauthorized access.");
        }

        var teacher = await _context.TeacherProfiles
            .FirstOrDefaultAsync(t => t.UserId == userId, cancellationToken);

        if (teacher == null)
        {
            return Result<List<ClassroomDto>>.Failure("User is not registered as a teacher.");
        }

        var classrooms = await _context.Classrooms
            .Where(c => c.TeacherId == teacher.Id && c.Status != ClassroomStatus.Deleted)
            .Include(c => c.Enrollments)
            .Select(c => new ClassroomDto
            {
                Id = c.Id,
                Name = c.Name,
                Subject = c.Subject,
                SubjectName = c.Subject.ToString(),
                Description = c.Description,
                AgeGroup = c.AgeGroup,
                SchoolYear = c.SchoolYear,
                Schedule = c.Schedule,
                ThemeColor = c.ThemeColor,
                MaxLearners = c.MaxLearners,
                Status = c.Status,
                EnrolledCount = c.Enrollments.Count
            })
            .ToListAsync(cancellationToken);

        return Result<List<ClassroomDto>>.Success(classrooms);
    }
}

public class ClassroomDto
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public SubjectPreset Subject { get; set; }
    public string SubjectName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? AgeGroup { get; set; }
    public string? SchoolYear { get; set; }
    public string? Schedule { get; set; }
    public string? ThemeColor { get; set; }
    public int MaxLearners { get; set; }
    public ClassroomStatus Status { get; set; }
    public int EnrolledCount { get; set; }
}
