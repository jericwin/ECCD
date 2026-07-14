using ECCD.Domain.Common;
using ECCD.Domain.Enums;

namespace ECCD.Domain.Entities;

/// <summary>
/// Daily attendance record per learner per classroom.
/// Per PRD §9.
/// </summary>
public class Attendance : BaseEntity
{
    public Guid LearnerId { get; set; }
    public Guid ClassroomId { get; set; }
    public DateOnly Date { get; set; }
    public AttendanceStatus Status { get; set; }
    public string? Remarks { get; set; }

    // Navigation
    public Learner Learner { get; set; } = null!;
    public Classroom Classroom { get; set; } = null!;
}
