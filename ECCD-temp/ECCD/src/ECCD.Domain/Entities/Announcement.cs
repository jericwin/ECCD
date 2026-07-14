using ECCD.Domain.Common;
using ECCD.Domain.Enums;

namespace ECCD.Domain.Entities;

/// <summary>
/// Announcement — classroom-scoped or center-wide.
/// Per PRD FR-10.1.
/// </summary>
public class Announcement : AuditableEntity
{
    public string Title { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public AnnouncementScope Scope { get; set; }
    public string AuthorId { get; set; } = string.Empty;
    public Guid? ClassroomId { get; set; }
    public Guid? CdcId { get; set; }

    // Navigation
    public Classroom? Classroom { get; set; }
    public ChildDevelopmentCenter? Cdc { get; set; }
}
