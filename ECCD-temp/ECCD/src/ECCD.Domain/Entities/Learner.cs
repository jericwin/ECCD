using ECCD.Domain.Common;
using ECCD.Domain.Enums;
using ECCD.Domain.Interfaces;

namespace ECCD.Domain.Entities;

/// <summary>
/// Learner (child) record. Contains PII and health-linked data — treat as sensitive.
/// Per PRD §9 + FR-6.
/// </summary>
public class Learner : AuditableEntity, ISoftDeletable
{
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string? PhotoUrl { get; set; }
    public DateTime Birthdate { get; set; }
    public Gender Gender { get; set; }
    public string LearnerIdCode { get; set; } = string.Empty;

    // Foreign keys
    public Guid ParentId { get; set; }
    public Guid CdcId { get; set; }

    // Soft delete
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAt { get; set; }

    // Navigation
    public ParentProfile Parent { get; set; } = null!;
    public ChildDevelopmentCenter Cdc { get; set; } = null!;
    public ICollection<ClassroomEnrollment> Enrollments { get; set; } = new List<ClassroomEnrollment>();
    public ICollection<Attendance> AttendanceRecords { get; set; } = new List<Attendance>();
    public ICollection<BMIRecord> BmiRecords { get; set; } = new List<BMIRecord>();
    public ICollection<ImmunizationRecord> ImmunizationRecords { get; set; } = new List<ImmunizationRecord>();
    public ICollection<Submission> Submissions { get; set; } = new List<Submission>();
    public ICollection<RiskFlag> RiskFlags { get; set; } = new List<RiskFlag>();
    public ICollection<GrowthAssessment> GrowthAssessments { get; set; } = new List<GrowthAssessment>();

    /// <summary>
    /// Computed full name.
    /// </summary>
    public string FullName => $"{FirstName} {LastName}";
}
