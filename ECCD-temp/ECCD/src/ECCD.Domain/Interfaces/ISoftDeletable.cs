namespace ECCD.Domain.Interfaces;

/// <summary>
/// Marker interface for entities that support soft-delete.
/// Infrastructure layer intercepts delete operations for these entities.
/// </summary>
public interface ISoftDeletable
{
    bool IsDeleted { get; set; }
    DateTime? DeletedAt { get; set; }
}
