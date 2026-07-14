using ECCD.Domain.Common;

namespace ECCD.Domain.Entities;

/// <summary>
/// Junction entity linking a Learner to a Classroom.
/// </summary>
public class ClassroomEnrollment : BaseEntity
{
    public Guid ClassroomId { get; set; }
    public Guid LearnerId { get; set; }
    public DateTime EnrolledAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public Classroom Classroom { get; set; } = null!;
    public Learner Learner { get; set; } = null!;
}
