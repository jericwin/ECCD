using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Entities;
using ECCD.Infrastructure.Identity;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Infrastructure.Persistence;

/// <summary>
/// Main EF Core DbContext — inherits IdentityDbContext for ASP.NET Core Identity tables
/// and implements IApplicationDbContext for the application layer.
/// </summary>
public class ApplicationDbContext : IdentityDbContext<ApplicationUser, ApplicationRole, string>, IApplicationDbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options) { }

    // Domain entities
    public DbSet<ChildDevelopmentCenter> ChildDevelopmentCenters => Set<ChildDevelopmentCenter>();
    public DbSet<TeacherProfile> TeacherProfiles => Set<TeacherProfile>();
    public DbSet<ParentProfile> ParentProfiles => Set<ParentProfile>();
    public DbSet<Learner> Learners => Set<Learner>();
    public DbSet<Classroom> Classrooms => Set<Classroom>();
    public DbSet<ClassroomEnrollment> ClassroomEnrollments => Set<ClassroomEnrollment>();
    public DbSet<Post> Posts => Set<Post>();
    public DbSet<ClassworkFolder> ClassworkFolders => Set<ClassworkFolder>();
    public DbSet<ClassworkItem> ClassworkItems => Set<ClassworkItem>();
    public DbSet<Submission> Submissions => Set<Submission>();
    public DbSet<Attendance> Attendances => Set<Attendance>();
    public DbSet<BMIRecord> BmiRecords => Set<BMIRecord>();
    public DbSet<ImmunizationRecord> ImmunizationRecords => Set<ImmunizationRecord>();
    public DbSet<GrowthAssessment> GrowthAssessments => Set<GrowthAssessment>();
    public DbSet<RiskFlag> RiskFlags => Set<RiskFlag>();
    public DbSet<Announcement> Announcements => Set<Announcement>();
    public DbSet<Report> Reports => Set<Report>();
    public DbSet<AuditLog> AuditLogs => Set<AuditLog>();
    public DbSet<ConsentRecord> ConsentRecords => Set<ConsentRecord>();

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);

        // Apply all configurations from this assembly
        builder.ApplyConfigurationsFromAssembly(typeof(ApplicationDbContext).Assembly);

        // Seed mock Child Development Centers (CDCs)
        builder.Entity<ChildDevelopmentCenter>().HasData(
            new ChildDevelopmentCenter
            {
                Id = Guid.Parse("11111111-1111-1111-1111-111111111111"),
                Name = "CDC Barangay Central",
                Address = "Poblacion, Barangay Central",
                CreatedAt = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc)
            },
            new ChildDevelopmentCenter
            {
                Id = Guid.Parse("22222222-2222-2222-2222-222222222222"),
                Name = "CDC Barangay East",
                Address = "Eastside, Barangay East",
                CreatedAt = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc)
            }
        );
    }
}
