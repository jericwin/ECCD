namespace ECCD.Domain.Common;

/// <summary>
/// Extends BaseEntity with user-level audit fields (who created/updated).
/// Use for entities where tracking the responsible user matters.
/// </summary>
public abstract class AuditableEntity : BaseEntity
{
    public string? CreatedBy { get; set; }
    public string? UpdatedBy { get; set; }
}
