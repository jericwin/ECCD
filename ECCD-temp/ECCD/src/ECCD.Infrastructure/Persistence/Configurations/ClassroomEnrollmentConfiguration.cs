using ECCD.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace ECCD.Infrastructure.Persistence.Configurations;

public class ClassroomEnrollmentConfiguration : IEntityTypeConfiguration<ClassroomEnrollment>
{
    public void Configure(EntityTypeBuilder<ClassroomEnrollment> builder)
    {
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => new { e.ClassroomId, e.LearnerId }).IsUnique();

        builder.HasOne(e => e.Classroom)
            .WithMany(c => c.Enrollments)
            .HasForeignKey(e => e.ClassroomId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(e => e.Learner)
            .WithMany(l => l.Enrollments)
            .HasForeignKey(e => e.LearnerId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
