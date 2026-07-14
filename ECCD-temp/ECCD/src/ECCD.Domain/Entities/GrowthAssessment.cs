using ECCD.Domain.Common;

namespace ECCD.Domain.Entities;

/// <summary>
/// Predictive output — growth trend assessment for a learner.
/// Per PRD §9 + §10 Phase 1.
/// </summary>
public class GrowthAssessment : BaseEntity
{
    public Guid LearnerId { get; set; }
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    public string TrendDirection { get; set; } = string.Empty; // e.g., "improving", "declining", "stable"
    public string RiskLevel { get; set; } = string.Empty;
    public string Basis { get; set; } = string.Empty; // explanation of how the assessment was computed

    // Navigation
    public Learner Learner { get; set; } = null!;
}
