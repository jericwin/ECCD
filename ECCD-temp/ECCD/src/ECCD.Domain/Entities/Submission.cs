using ECCD.Domain.Common;
using ECCD.Domain.Enums;

namespace ECCD.Domain.Entities;

/// <summary>
/// Learner submission for a classwork item.
/// Per PRD §9.
/// </summary>
public class Submission : AuditableEntity
{
    public Guid ClassworkItemId { get; set; }
    public Guid LearnerId { get; set; }
    public decimal? Score { get; set; }
    public SubmissionStatus Status { get; set; } = SubmissionStatus.NotSubmitted;
    public string? Remarks { get; set; }

    // Navigation
    public ClassworkItem ClassworkItem { get; set; } = null!;
    public Learner Learner { get; set; } = null!;
}
