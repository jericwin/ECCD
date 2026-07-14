using ECCD.Application.Common.Interfaces;
using ECCD.Application.Common.Models;
using ECCD.Domain.Common;
using ECCD.Domain.Enums;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Learners.Queries;

public record GetLearnersQuery : IRequest<Result<PagedResult<LearnerDto>>>
{
    public string? SearchQuery { get; init; }
    public Guid? ClassroomId { get; init; }
    public Gender? Gender { get; init; }
    public int Page { get; init; } = 1;
    public int PageSize { get; init; } = 10;
}

public class GetLearnersQueryHandler : IRequestHandler<GetLearnersQuery, Result<PagedResult<LearnerDto>>>
{
    private readonly IApplicationDbContext _context;
    private readonly ICurrentUserService _currentUserService;

    public GetLearnersQueryHandler(IApplicationDbContext context, ICurrentUserService currentUserService)
    {
        _context = context;
        _currentUserService = currentUserService;
    }

    public async Task<Result<PagedResult<LearnerDto>>> Handle(GetLearnersQuery request, CancellationToken cancellationToken)
    {
        var userId = _currentUserService.UserId;
        if (string.IsNullOrEmpty(userId))
        {
            return Result<PagedResult<LearnerDto>>.Failure("Unauthorized access.");
        }

        var query = _context.Learners
            .Include(l => l.Parent)
            .Include(l => l.Enrollments)
            .AsQueryable();

        // Enforce RBAC logic based on user role (PRD §8.2)
        var userRole = _currentUserService.Roles.FirstOrDefault();
        if (userRole == "Parent")
        {
            var parent = await _context.ParentProfiles
                .FirstOrDefaultAsync(p => p.UserId == userId, cancellationToken);
            if (parent == null)
            {
                return Result<PagedResult<LearnerDto>>.Failure("Parent profile not found.");
            }
            query = query.Where(l => l.ParentId == parent.Id);
        }
        else if (userRole == "Teacher" || userRole == "Administrator")
        {
            var teacher = await _context.TeacherProfiles
                .FirstOrDefaultAsync(t => t.UserId == userId, cancellationToken);
            if (teacher == null)
            {
                return Result<PagedResult<LearnerDto>>.Failure("Teacher profile not found.");
            }
            // Scoped to the teacher's CDC (PRD FR-2.4)
            if (teacher.CdcId.HasValue)
            {
                query = query.Where(l => l.CdcId == teacher.CdcId.Value);
            }
        }

        // Apply filters
        if (!string.IsNullOrEmpty(request.SearchQuery))
        {
            var search = request.SearchQuery.ToLower();
            query = query.Where(l => 
                l.FirstName.ToLower().Contains(search) || 
                l.LastName.ToLower().Contains(search) || 
                l.LearnerIdCode.ToLower().Contains(search) ||
                l.Parent.FullName.ToLower().Contains(search)
            );
        }

        if (request.ClassroomId.HasValue)
        {
            query = query.Where(l => l.Enrollments.Any(e => e.ClassroomId == request.ClassroomId.Value));
        }

        if (request.Gender.HasValue)
        {
            query = query.Where(l => l.Gender == request.Gender.Value);
        }

        // Pagination
        var totalCount = await query.CountAsync(cancellationToken);
        
        var items = await query
            .OrderBy(l => l.LastName)
            .ThenBy(l => l.FirstName)
            .Skip((request.Page - 1) * request.PageSize)
            .Take(request.PageSize)
            .Select(l => new LearnerDto
            {
                Id = l.Id,
                FirstName = l.FirstName,
                LastName = l.LastName,
                FullName = l.FirstName + " " + l.LastName,
                PhotoUrl = l.PhotoUrl,
                Birthdate = l.Birthdate,
                Gender = l.Gender,
                LearnerIdCode = l.LearnerIdCode,
                ParentId = l.ParentId,
                ParentName = l.Parent.FullName,
                CdcId = l.CdcId
            })
            .ToListAsync(cancellationToken);

        var paged = new PagedResult<LearnerDto>
        {
            Items = items,
            Page = request.Page,
            PageSize = request.PageSize,
            TotalCount = totalCount
        };

        return Result<PagedResult<LearnerDto>>.Success(paged);
    }
}

public class LearnerDto
{
    public Guid Id { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string? PhotoUrl { get; set; }
    public DateTime Birthdate { get; set; }
    public Gender Gender { get; set; }
    public string LearnerIdCode { get; set; } = string.Empty;
    public Guid ParentId { get; set; }
    public string ParentName { get; set; } = string.Empty;
    public Guid CdcId { get; set; }
}
