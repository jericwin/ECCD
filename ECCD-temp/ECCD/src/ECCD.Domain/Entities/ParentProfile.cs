using ECCD.Domain.Common;

namespace ECCD.Domain.Entities;

/// <summary>
/// Parent profile linked to the Identity user.
/// Fields per PRD FR-1.5.
/// </summary>
public class ParentProfile : AuditableEntity
{
    public string UserId { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string RelationshipToLearner { get; set; } = string.Empty;
    public string? Mobile { get; set; }
    public string? Address { get; set; }

    // Navigation
    public ICollection<Learner> Learners { get; set; } = new List<Learner>();
}
