using ECCD.Domain.Common;
using ECCD.Domain.Enums;

namespace ECCD.Domain.Entities;

/// <summary>
/// Individual classwork item (activity, assignment, assessment, etc.).
/// Per PRD FR-5.2.
/// </summary>
public class ClassworkItem : AuditableEntity
{
    public Guid FolderId { get; set; }
    public ClassworkType Type { get; set; }
    public ClassworkItemStatus Status { get; set; } = ClassworkItemStatus.Draft;
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? AttachmentUrl { get; set; }
    public DateTime? DueDate { get; set; }
    public int? MaxScore { get; set; }

    // Navigation
    public ClassworkFolder Folder { get; set; } = null!;
    public ICollection<Submission> Submissions { get; set; } = new List<Submission>();
}
