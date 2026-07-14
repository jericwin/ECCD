using ECCD.Domain.Common;

namespace ECCD.Domain.Entities;

/// <summary>
/// Generated report record. Per PRD FR-11.
/// </summary>
public class Report : BaseEntity
{
    public Guid? LearnerId { get; set; }
    public Guid? ClassroomId { get; set; }
    public string Type { get; set; } = string.Empty; // e.g., "growth", "attendance", "progress"
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    public string? FileUrl { get; set; }
    public string GeneratedBy { get; set; } = string.Empty;

    // Navigation
    public Learner? Learner { get; set; }
    public Classroom? Classroom { get; set; }
}
