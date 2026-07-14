using ECCD.Domain.Common;

namespace ECCD.Domain.Entities;

/// <summary>
/// Consent record — logs timestamped privacy consent per PRD §8.2.
/// Not just a boolean; stores when and how consent was given.
/// </summary>
public class ConsentRecord : BaseEntity
{
    public string UserId { get; set; } = string.Empty;
    public string ConsentType { get; set; } = string.Empty; // e.g., "TermsOfService", "PrivacyPolicy", "DataProcessing"
    public DateTime ConsentedAt { get; set; } = DateTime.UtcNow;
    public string? IpAddress { get; set; }
    public string? UserAgent { get; set; }
    public bool IsWithdrawn { get; set; }
    public DateTime? WithdrawnAt { get; set; }
}
