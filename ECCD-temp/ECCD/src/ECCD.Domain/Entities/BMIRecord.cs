using ECCD.Domain.Common;
using ECCD.Domain.Enums;

namespace ECCD.Domain.Entities;

/// <summary>
/// BMI measurement record. Sensitive health data — per PRD FR-7.1, §8.2.
/// BMI-for-age computed against WHO Child Growth Standards.
/// </summary>
public class BMIRecord : AuditableEntity
{
    public Guid LearnerId { get; set; }
    public DateOnly Date { get; set; }
    public decimal HeightCm { get; set; }
    public decimal WeightKg { get; set; }
    public decimal Bmi { get; set; }
    public decimal? WhoZScore { get; set; }
    public BmiStatus Status { get; set; }

    // Navigation
    public Learner Learner { get; set; } = null!;
}
