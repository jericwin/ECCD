using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Classrooms.Queries;

public record GetClassroomByIdQuery(Guid Id) : IRequest<Result<ClassroomDto>>;

public class GetClassroomByIdQueryHandler : IRequestHandler<GetClassroomByIdQuery, Result<ClassroomDto>>
{
    private readonly IApplicationDbContext _context;
    private readonly ICurrentUserService _currentUserService;

    public GetClassroomByIdQueryHandler(IApplicationDbContext context, ICurrentUserService currentUserService)
    {
        _context = context;
        _currentUserService = currentUserService;
    }

    public async Task<Result<ClassroomDto>> Handle(GetClassroomByIdQuery request, CancellationToken cancellationToken)
    {
        var userId = _currentUserService.UserId;
        if (string.IsNullOrEmpty(userId))
        {
            return Result<ClassroomDto>.Failure("Unauthorized access.");
        }

        // Fetch classroom
        var c = await _context.Classrooms
            .Include(x => x.Enrollments)
            .FirstOrDefaultAsync(x => x.Id == request.Id, cancellationToken);

        if (c == null)
        {
            return Result<ClassroomDto>.Failure("Classroom not found.");
        }

        // Enforce boundary: only the classroom's teacher or a linked parent can view classroom details
        var teacher = await _context.TeacherProfiles
            .FirstOrDefaultAsync(t => t.UserId == userId, cancellationToken);

        var isAuthorized = false;

        if (teacher != null && c.TeacherId == teacher.Id)
        {
            isAuthorized = true;
        }
        else
        {
            // Check if user is parent of an enrolled learner in this classroom
            var parent = await _context.ParentProfiles
                .FirstOrDefaultAsync(p => p.UserId == userId, cancellationToken);
            
            if (parent != null)
            {
                var isEnrolled = await _context.ClassroomEnrollments
                    .Include(e => e.Learner)
                    .AnyAsync(e => e.ClassroomId == c.Id && e.Learner.ParentId == parent.Id, cancellationToken);

                if (isEnrolled)
                {
                    isAuthorized = true;
                }
            }
        }

        if (!isAuthorized)
        {
            return Result<ClassroomDto>.Failure("You do not have permission to view this classroom.");
        }

        var dto = new ClassroomDto
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
        };

        return Result<ClassroomDto>.Success(dto);
    }
}
