using ECCD.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Common.Interfaces;

/// <summary>
/// Abstraction over the EF Core DbContext. Defined in Application layer,
/// implemented in Infrastructure. Controllers and handlers depend on this,
/// never on the concrete DbContext directly.
/// </summary>
public interface IApplicationDbContext
{
    DbSet<ChildDevelopmentCenter> ChildDevelopmentCenters { get; }
    DbSet<TeacherProfile> TeacherProfiles { get; }
    DbSet<ParentProfile> ParentProfiles { get; }
    DbSet<Learner> Learners { get; }
    DbSet<Classroom> Classrooms { get; }
    DbSet<ClassroomEnrollment> ClassroomEnrollments { get; }
    DbSet<Post> Posts { get; }
    DbSet<ClassworkFolder> ClassworkFolders { get; }
    DbSet<ClassworkItem> ClassworkItems { get; }
    DbSet<Submission> Submissions { get; }
    DbSet<Attendance> Attendances { get; }
    DbSet<BMIRecord> BmiRecords { get; }
    DbSet<ImmunizationRecord> ImmunizationRecords { get; }
    DbSet<GrowthAssessment> GrowthAssessments { get; }
    DbSet<RiskFlag> RiskFlags { get; }
    DbSet<Announcement> Announcements { get; }
    DbSet<Report> Reports { get; }
    DbSet<AuditLog> AuditLogs { get; }
    DbSet<ConsentRecord> ConsentRecords { get; }

    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
}
