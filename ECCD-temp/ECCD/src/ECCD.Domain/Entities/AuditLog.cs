using ECCD.Domain.Common;

namespace ECCD.Domain.Entities;

/// <summary>
/// Audit log — who viewed/edited a learner's health record and when.
/// Required by PRD §8.2 for data privacy compliance.
/// </summary>
public class AuditLog : BaseEntity
{
    public string UserId { get; set; } = string.Empty;
    public string Action { get; set; } = string.Empty; // e.g., "View", "Create", "Update", "Delete"
    public string EntityType { get; set; } = string.Empty; // e.g., "BMIRecord", "Learner"
    public string EntityId { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string? Details { get; set; }
}
