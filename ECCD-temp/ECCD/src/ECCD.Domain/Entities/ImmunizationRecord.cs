using ECCD.Domain.Common;
using ECCD.Domain.Enums;

namespace ECCD.Domain.Entities;

/// <summary>
/// Immunization record per learner per vaccine dose.
/// Tracked against DOH EPI schedule. Per PRD FR-7.2.
/// </summary>
public class ImmunizationRecord : AuditableEntity
{
    public Guid LearnerId { get; set; }
    public string Vaccine { get; set; } = string.Empty;
    public int DoseNumber { get; set; }
    public DateOnly? DateGiven { get; set; }
    public DateOnly? DueDate { get; set; }
    public ImmunizationStatus Status { get; set; }

    // Navigation
    public Learner Learner { get; set; } = null!;
}
