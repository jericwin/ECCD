using ECCD.Domain.Common;
using ECCD.Domain.Enums;

namespace ECCD.Domain.Entities;

/// <summary>
/// Subject-based folder within a classroom for organizing classwork.
/// Per PRD FR-5.2.
/// </summary>
public class ClassworkFolder : AuditableEntity
{
    public Guid ClassroomId { get; set; }
    public SubjectPreset Subject { get; set; }

    // Navigation
    public Classroom Classroom { get; set; } = null!;
    public ICollection<ClassworkItem> Items { get; set; } = new List<ClassworkItem>();
}
