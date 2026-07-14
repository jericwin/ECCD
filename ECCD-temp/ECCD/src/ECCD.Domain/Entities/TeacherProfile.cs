using ECCD.Domain.Common;

namespace ECCD.Domain.Entities;

/// <summary>
/// Teacher/Administrator profile linked to the Identity user.
/// Fields per PRD FR-1.4.
/// </summary>
public class TeacherProfile : AuditableEntity
{
    public string UserId { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string EmployeeId { get; set; } = string.Empty;
    public string Position { get; set; } = string.Empty;
    public string? ProfilePhotoUrl { get; set; }
    public string? Mobile { get; set; }
    public string? Address { get; set; }
    public Guid? CdcId { get; set; }

    // Navigation
    public ChildDevelopmentCenter? Cdc { get; set; }
    public ICollection<Classroom> Classrooms { get; set; } = new List<Classroom>();
}
