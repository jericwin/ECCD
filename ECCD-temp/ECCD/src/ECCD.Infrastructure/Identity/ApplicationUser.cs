using Microsoft.AspNetCore.Identity;

namespace ECCD.Infrastructure.Identity;

/// <summary>
/// Application user extending ASP.NET Core Identity's IdentityUser.
/// Links to TeacherProfile or ParentProfile based on role.
/// </summary>
public class ApplicationUser : IdentityUser
{
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? ProfilePhotoUrl { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? UpdatedAt { get; set; }
    public bool IsActive { get; set; } = true;

    /// <summary>
    /// Stores the GUID of the corresponding TeacherProfile or ParentProfile.
    /// </summary>
    public Guid? ProfileId { get; set; }
}
