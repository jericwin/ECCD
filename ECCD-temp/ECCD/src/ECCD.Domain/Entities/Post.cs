using ECCD.Domain.Common;
using ECCD.Domain.Enums;

namespace ECCD.Domain.Entities;

/// <summary>
/// Stream post within a classroom. Per PRD FR-5.1.
/// </summary>
public class Post : AuditableEntity
{
    public Guid ClassroomId { get; set; }
    public string AuthorId { get; set; } = string.Empty;
    public PostType Type { get; set; }
    public string? Title { get; set; }
    public string Content { get; set; } = string.Empty;
    public bool IsPinned { get; set; }

    // Navigation
    public Classroom Classroom { get; set; } = null!;
}
