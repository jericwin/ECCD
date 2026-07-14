namespace ECCD.Domain.Interfaces;

/// <summary>
/// Unit of Work pattern — coordinates saving changes across multiple repositories.
/// </summary>
public interface IUnitOfWork : IDisposable
{
    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
}
