using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Learners.Queries;

public record GetLearnerByIdQuery(Guid Id) : IRequest<Result<LearnerDetailDto>>;

public class GetLearnerByIdQueryHandler : IRequestHandler<GetLearnerByIdQuery, Result<LearnerDetailDto>>
{
    private readonly IApplicationDbContext _context;
    private readonly ICurrentUserService _currentUserService;

    public GetLearnerByIdQueryHandler(IApplicationDbContext context, ICurrentUserService currentUserService)
    {
        _context = context;
        _currentUserService = currentUserService;
    }

    public async Task<Result<LearnerDetailDto>> Handle(GetLearnerByIdQuery request, CancellationToken cancellationToken)
    {
        var userId = _currentUserService.UserId;
        if (string.IsNullOrEmpty(userId))
        {
            return Result<LearnerDetailDto>.Failure("Unauthorized access.");
        }

        var learner = await _context.Learners
            .Include(l => l.Parent)
            .Include(l => l.Cdc)
            .Include(l => l.Enrollments)
                .ThenInclude(e => e.Classroom)
            .FirstOrDefaultAsync(l => l.Id == request.Id, cancellationToken);

        if (learner == null)
        {
            return Result<LearnerDetailDto>.Failure("Learner not found.");
        }

        // RBAC validation
        var userRole = _currentUserService.Roles.FirstOrDefault();
        var isAuthorized = false;

        if (userRole == "Parent")
        {
            var parent = await _context.ParentProfiles
                .FirstOrDefaultAsync(p => p.UserId == userId, cancellationToken);
            if (parent != null && learner.ParentId == parent.Id)
            {
                isAuthorized = true;
            }
        }
        else if (userRole == "Teacher" || userRole == "Administrator")
        {
            var teacher = await _context.TeacherProfiles
                .FirstOrDefaultAsync(t => t.UserId == userId, cancellationToken);
            if (teacher != null && learner.CdcId == teacher.CdcId)
            {
                isAuthorized = true;
            }
        }

        if (!isAuthorized)
        {
            return Result<LearnerDetailDto>.Failure("You do not have permission to view this learner record.");
        }

        var enrolledClasses = learner.Enrollments.Select(e => new EnrolledClassroomDto
        {
            ClassroomId = e.ClassroomId,
            ClassroomName = e.Classroom.Name,
            Subject = e.Classroom.Subject.ToString(),
            SchoolYear = e.Classroom.SchoolYear,
            EnrolledAt = e.EnrolledAt
        }).ToList();

        var dto = new LearnerDetailDto
        {
            Id = learner.Id,
            FirstName = learner.FirstName,
            LastName = learner.LastName,
            FullName = learner.FullName,
            PhotoUrl = learner.PhotoUrl,
            Birthdate = learner.Birthdate,
            Gender = learner.Gender.ToString(),
            LearnerIdCode = learner.LearnerIdCode,
            ParentId = learner.ParentId,
            ParentName = learner.Parent.FullName,
            ParentMobile = learner.Parent.Mobile,
            ParentAddress = learner.Parent.Address,
            CdcId = learner.CdcId,
            CdcName = learner.Cdc.Name,
            EnrolledClassrooms = enrolledClasses
        };

        return Result<LearnerDetailDto>.Success(dto);
    }
}

public class LearnerDetailDto
{
    public Guid Id { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string? PhotoUrl { get; set; }
    public DateTime Birthdate { get; set; }
    public string Gender { get; set; } = string.Empty;
    public string LearnerIdCode { get; set; } = string.Empty;
    public Guid ParentId { get; set; }
    public string ParentName { get; set; } = string.Empty;
    public string? ParentMobile { get; set; }
    public string? ParentAddress { get; set; }
    public Guid CdcId { get; set; }
    public string CdcName { get; set; } = string.Empty;
    public List<EnrolledClassroomDto> EnrolledClassrooms { get; set; } = new();
}

public class EnrolledClassroomDto
{
    public Guid ClassroomId { get; set; }
    public string ClassroomName { get; set; } = string.Empty;
    public string Subject { get; set; } = string.Empty;
    public string? SchoolYear { get; set; }
    public DateTime EnrolledAt { get; set; }
}
