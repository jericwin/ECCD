using ECCD.Domain.Common;

namespace ECCD.Domain.Entities;

/// <summary>
/// Child Development Center — the institution that operates classrooms.
/// </summary>
public class ChildDevelopmentCenter : AuditableEntity
{
    public string Name { get; set; } = string.Empty;
    public string Address { get; set; } = string.Empty;

    // Navigation
    public ICollection<Classroom> Classrooms { get; set; } = new List<Classroom>();
    public ICollection<Learner> Learners { get; set; } = new List<Learner>();
}
