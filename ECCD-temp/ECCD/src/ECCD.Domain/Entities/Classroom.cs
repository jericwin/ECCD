using ECCD.Domain.Common;
using ECCD.Domain.Enums;
using ECCD.Domain.Interfaces;

namespace ECCD.Domain.Entities;

/// <summary>
/// Classroom managed by a teacher within a CDC.
/// Per PRD FR-4.1.
/// </summary>
public class Classroom : AuditableEntity, ISoftDeletable
{
    public string Name { get; set; } = string.Empty;
    public SubjectPreset Subject { get; set; }
    public string? Description { get; set; }
    public string? AgeGroup { get; set; }
    public string? SchoolYear { get; set; }
    public string? Schedule { get; set; }
    public string? ThemeColor { get; set; }
    public string? BannerUrl { get; set; }
    public int MaxLearners { get; set; } = 30;
    public ClassroomStatus Status { get; set; } = ClassroomStatus.Draft;

    // Foreign keys
    public Guid TeacherId { get; set; }
    public Guid? CdcId { get; set; }

    // Soft delete
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAt { get; set; }

    // Navigation
    public TeacherProfile Teacher { get; set; } = null!;
    public ChildDevelopmentCenter? Cdc { get; set; }
    public ICollection<ClassroomEnrollment> Enrollments { get; set; } = new List<ClassroomEnrollment>();
    public ICollection<Post> Posts { get; set; } = new List<Post>();
    public ICollection<ClassworkFolder> ClassworkFolders { get; set; } = new List<ClassworkFolder>();
    public ICollection<Attendance> AttendanceRecords { get; set; } = new List<Attendance>();
    public ICollection<Announcement> Announcements { get; set; } = new List<Announcement>();
}
