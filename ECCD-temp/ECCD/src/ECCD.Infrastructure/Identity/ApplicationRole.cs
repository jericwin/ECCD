using Microsoft.AspNetCore.Identity;

namespace ECCD.Infrastructure.Identity;

/// <summary>
/// Application role extending ASP.NET Core Identity's IdentityRole.
/// </summary>
public class ApplicationRole : IdentityRole
{
    public ApplicationRole() : base() { }
    public ApplicationRole(string roleName) : base(roleName) { }
    public string? Description { get; set; }
}
