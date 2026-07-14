namespace ECCD.Application.Common.Interfaces;

/// <summary>
/// DateTime abstraction for testability.
/// </summary>
public interface IDateTimeService
{
    DateTime UtcNow { get; }
    DateOnly Today { get; }
}
