using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using ECCD.Domain.Enums;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Classrooms.Commands;

public record ArchiveClassroomCommand(Guid Id) : IRequest<Result>;

public class ArchiveClassroomCommandHandler : IRequestHandler<ArchiveClassroomCommand, Result>
{
    private readonly IApplicationDbContext _context;
    private readonly ICurrentUserService _currentUserService;

    public ArchiveClassroomCommandHandler(IApplicationDbContext context, ICurrentUserService currentUserService)
    {
        _context = context;
        _currentUserService = currentUserService;
    }

    public async Task<Result> Handle(ArchiveClassroomCommand request, CancellationToken cancellationToken)
    {
        var classroom = await _context.Classrooms
            .FirstOrDefaultAsync(c => c.Id == request.Id, cancellationToken);

        if (classroom == null)
        {
            return Result.Failure("Classroom not found.");
        }

        // Verify ownership
        var userId = _currentUserService.UserId;
        var teacher = await _context.TeacherProfiles
            .FirstOrDefaultAsync(t => t.UserId == userId, cancellationToken);

        if (teacher == null || classroom.TeacherId != teacher.Id)
        {
            return Result.Failure("You do not have permission to archive this classroom.");
        }

        classroom.Status = ClassroomStatus.Archived;
        await _context.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }
}
